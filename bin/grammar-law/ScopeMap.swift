import Foundation

// vi owns this closed data format. It is Swift-shaped metadata, never executed.
// Paths are source-repository-relative, not resolver/cache addresses.
struct GrammarScopeMap {
    struct Entry: Codable, Equatable { let prefix: String
     let scope: String }
    let entries: [Entry]
    struct Refusal: Error, CustomStringConvertible {
        let description: String
        init(_ text: String) { description = text }
    }

    static func sourcePath(_ path: String) -> Bool {
        !path.isEmpty && !path.hasPrefix("/") && !path.contains("\\")
            && !path.contains(":") && !path.split(separator: "/", omittingEmptySubsequences: false)
                .contains { $0.isEmpty || $0 == "." || $0 == ".." }
    }

    static func read(_ source: String, scopes: Set<String>) throws -> GrammarScopeMap {
        // Only this declaration is data. Unknown fields, Swift interpolation,
        // executable expressions and partially read maps are not accepted.
        let ns = source as NSString
        let pattern = #"//[^\n]*|/\*(?:[^*]|\*(?!/))*\*/|\"(?:[^\"\\\n]|\\[\"\\/bfnrt]|\\u[0-9a-fA-F]{4})*\"|[A-Za-z_][A-Za-z_0-9]*|[^\s]"#
        let re = try NSRegularExpression(pattern: pattern)
        var tokens: [String] = []
        var consumed = 0
        for hit in re.matches(in: source, range: NSRange(location: 0, length: ns.length)) {
            if !ns.substring(with: NSRange(location: consumed, length: hit.range.location - consumed))
                .trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                throw Refusal("scope map contains unread syntax")
            }
            let token = ns.substring(with: hit.range)
            if !token.hasPrefix("//") && !token.hasPrefix("/*") { tokens.append(token) }
            consumed = hit.range.location + hit.range.length
        }
        if !ns.substring(from: consumed).trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
            throw Refusal("scope map contains unread syntax")
        }
        var i = 0
        func take(_ word: String) throws {
            guard i < tokens.count, tokens[i] == word else {
                throw Refusal("scope map expected '\(word)' at token \(i + 1)")
            }
            i += 1
        }
        func string() throws -> String {
            guard i < tokens.count, let bytes = tokens[i].data(using: .utf8),
                  let value = try? JSONSerialization.jsonObject(with: bytes, options: .fragmentsAllowed) as? String else {
                throw Refusal("scope map expected a literal string at token \(i + 1)")
            }
            i += 1
            return value
        }
        for token in ["public", "enum", "GrammarScopes", "{", "public", "static", "let", "format", "="] { try take(token) }
        guard try string() == "vi-scope-map/1" else { throw Refusal("unsupported scope map format") }
        for token in ["public", "static", "let", "entries", ":", "[", "(", "String", ",", "String", ")", "]", "=", "["] { try take(token) }
        var entries: [Entry] = []
        while i < tokens.count, tokens[i] != "]" {
            try take("(")
            let prefix = try string()
            try take(",")
            let scope = try string()
            try take(")")
            guard sourcePath(prefix) else { throw Refusal("scope map has a non-relative source path '\(prefix)'") }
            guard scopes.contains(scope) else { throw Refusal("scope map names an unknown scope '\(scope)' at '\(prefix)'") }
            if let prior = entries.filter { $0.prefix == prefix }.first, prior.scope != scope {
                throw Refusal("scope map has conflicting equal prefixes '\(prefix)': \(prior.scope), \(scope)")
            }
            let entry = Entry(prefix: prefix, scope: scope)
            if !entries.contains(entry) { entries.append(entry) }
            if i < tokens.count, tokens[i] == "," { i += 1 }
            else if i < tokens.count, tokens[i] != "]" { throw Refusal("scope map expected ','") }
        }
        try take("]")
        try take("}")
        guard i == tokens.count, !entries.isEmpty else { throw Refusal("scope map is empty or has trailing syntax") }
        return GrammarScopeMap(entries: entries)
    }

    func scope(for path: String) throws -> String {
        guard Self.sourcePath(path) else { throw Refusal("non-relative source path '\(path)'") }
        let matches = entries.filter { path == $0.prefix || path.hasPrefix($0.prefix + "/") }
        guard let longest = matches.map({ $0.prefix.count }).max() else {
            throw Refusal("uncovered source path '\(path)'")
        }
        let scopes = Set(matches.filter { $0.prefix.count == longest }.map(\.scope))
        guard scopes.count == 1, let scope = scopes.first else {
            throw Refusal("conflicting scopes for '\(path)'")
        }
        return scope
    }
}

// SHA-256: the portable implementation also used by gate (46abce2).
func grammarSHA256(_ data: Data) -> String {
    // SHA-256, written out for the same reason SHA-1 above is: the vendored
    // judge states its digest and somebody has to be able to check it
    let k: [UInt32] = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
        0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
        0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
        0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
        0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
        0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]
    var h: [UInt32] = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                       0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
    var message = [UInt8](data)
    let bits = UInt64(message.count) * 8
    message.append(0x80)
    while message.count % 64 != 56 { message.append(0) }
    for i in (0..<8).reversed() { message.append(UInt8((bits >> (UInt64(i) * 8)) & 0xFF)) }
    func rot(_ x: UInt32, _ n: UInt32) -> UInt32 { return (x >> n) | (x << (32 - n)) }
    for chunk in stride(from: 0, to: message.count, by: 64) {
        var w = [UInt32](repeating: 0, count: 64)
        for i in 0..<16 {
            let o = chunk + i * 4
            w[i] = (UInt32(message[o]) << 24) | (UInt32(message[o + 1]) << 16)
                 | (UInt32(message[o + 2]) << 8) | UInt32(message[o + 3])
        }
        for i in 16..<64 {
            let s0 = rot(w[i - 15], 7) ^ rot(w[i - 15], 18) ^ (w[i - 15] >> 3)
            let s1 = rot(w[i - 2], 17) ^ rot(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w[i] = w[i - 16] &+ s0 &+ w[i - 7] &+ s1
        }
        var a = h[0], b = h[1], c = h[2], d = h[3]
        var e = h[4], f = h[5], g = h[6], hh = h[7]
        for i in 0..<64 {
            let s1 = rot(e, 6) ^ rot(e, 11) ^ rot(e, 25)
            let ch = (e & f) ^ (~e & g)
            let t1 = hh &+ s1 &+ ch &+ k[i] &+ w[i]
            let s0 = rot(a, 2) ^ rot(a, 13) ^ rot(a, 22)
            let mj = (a & b) ^ (a & c) ^ (b & c)
            let t2 = s0 &+ mj
            hh = g
            g = f
            f = e
            e = d &+ t1
            d = c
            c = b
            b = a
            a = t1 &+ t2
        }
        h[0] = h[0] &+ a
            h[1] = h[1] &+ b
            h[2] = h[2] &+ c
            h[3] = h[3] &+ d
        h[4] = h[4] &+ e
            h[5] = h[5] &+ f
            h[6] = h[6] &+ g
            h[7] = h[7] &+ hh
    }
    return h.map { String(format: "%08x", $0) }.joined()
}
