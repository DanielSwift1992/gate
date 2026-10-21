import Foundation

// The portable reading of the mirror consumes a census exported FROM the
// compiler's conformances. Neither a client nor this machine supplies grants.
// Linter still asks the Swift compiler; this reading is checked against it.
struct GrammarPolicy: Codable {
    struct Atom: Codable {
        let name: String
        let spelling: String
        let word: Bool
        let medium: Bool
        let opening: Bool
        let closes: String?
        let pairs: Bool
        let foreign: String?
        let escapes: Bool
        let declaration: Bool
        let builder: Bool
        let exempt: Bool
        let modifier: Bool
        let line: Bool
        let pair: Bool
        let grants: [String]
    }
    let format: String
    let scopes: [String]
    let defaultAtom: String
    let atoms: [Atom]
    let pairs: [String: [String]]

    struct Finding: Codable, Equatable { let line: Int
     let atom: String
     let scope: String
     let context: String }

    func findings(_ source: String, scope: String) throws -> [Finding] {
        guard format == "vi-grammar-policy/1", scopes.contains(scope),
              let fallback = atoms.filter { $0.name == defaultAtom }.first else {
            throw GrammarScopeMap.Refusal("unsupported grammar policy or scope '\(scope)'")
        }
        let chars = Array(source)
        var i = 0, line = 1
        let byName = Dictionary(uniqueKeysWithValues: atoms.map { ($0.name, $0) })
        let words = Dictionary(uniqueKeysWithValues: atoms.filter(\.word).map { ($0.spelling, $0) })
        let punctuation = atoms.filter { !$0.word && !$0.spelling.isEmpty }.sorted {
            if $0.spelling.count != $1.spelling.count { return $0.spelling.count > $1.spelling.count }
            return $0.name < $1.name
        }
        func identifier(_ c: Character) -> Bool { c.isLetter || c.isNumber || c == "_" }
        func starts(_ text: String) -> Bool {
            !text.isEmpty && chars[i...].starts(with: Array(text))
        }
        func advance(_ count: Int) {
            for _ in 0..<count
            where i < chars.count { if chars[i] == "\n" { line += 1 }
             i += 1 }
        }
        func next() -> (Atom?, String, Int) {
            let at = line
            guard i < chars.count else { return (nil, "Char0Atom", at) }
            if identifier(chars[i]) {
                let first = i
                while i < chars.count && identifier(chars[i]) { advance(1) }
                let word = String(chars[first..<i])
                let atom = words[word] ?? fallback
                return (atom, atom.name, at)
            }
            for atom in punctuation
            where starts(atom.spelling) {
                advance(atom.spelling.count)
                return (atom, atom.name, at)
            }
            let unknown = "Char\(chars[i].unicodeScalars.first?.value ?? 0)Atom"
            advance(1)
            return (nil, unknown, at)
        }
        // Follow the owner's raw Character consumption at an escape, including
        // balanced brackets and opaque foreign spans inside interpolation.
        // The boundary battery compares these rules with the typed mirror.
        let glyphs = Dictionary(uniqueKeysWithValues: punctuation.filter { $0.spelling.count == 1 }.map { (Character($0.spelling), $0) })
        func foreignHere() -> Atom? {
            for atom in punctuation
            where atom.foreign != nil && starts(atom.spelling) {
                advance(atom.spelling.count)
                return atom
            }
            return nil
        }
        func balanced(_ opener: Atom) {
            var depth = 0
            while i < chars.count {
                if let foreign = foreignHere() {
                    span(foreign)
                    continue
                }
                if let atom = glyphs[chars[i]] {
                    if atom.opening && atom.name == opener.name {
                        depth += 1
                        advance(1)
                        continue
                    }
                    if atom.closes == opener.name {
                        depth -= 1
                        advance(1)
                        if depth == 0 { return }
                        continue
                    }
                }
                advance(1)
            }
        }
        func span(_ atom: Atom) {
            guard let closeName = atom.foreign, let closer = byName[closeName] else { return }
            while i < chars.count {
                if starts(closer.spelling) {
                    advance(closer.spelling.count)
                    return
                }
                if glyphs[chars[i]]?.escapes == true {
                    advance(1)
                    guard i < chars.count else { return }
                    if let opening = glyphs[chars[i]], opening.opening {
                        balanced(opening)
                    } else { advance(1) }
                    continue
                }
                advance(1)
            }
        }
        struct Pending { let atom: String
         let grants: [String]
         let line: Int }
        struct Frame {
            let opener: String
         let context: String
            var pending: [Pending] }
        var frames = [Frame(opener: "", context: "Plain", pending: [])]
        var last: Atom? = fallback, head = true, lineHead = true, exempt = false
        var bad: [Finding] = []
        func finish(_ frame: Frame) {
            for p in frame.pending
            where frame.context != "Exempt" && !p.grants.contains(scope + "/" + frame.context) {
                bad.append(Finding(line: p.line, atom: p.atom, scope: scope, context: frame.context))
            }
            if frame.context == "Exempt" {
                // Exemption grants registered LintAtoms, never unknown chars.
                for p in frame.pending
                where byName[p.atom] == nil && pairs[p.atom] == nil && !p.atom.hasPrefix("Midline<") {
                    bad.append(Finding(line: p.line, atom: p.atom, scope: scope, context: frame.context))
                }
            }
        }
        func emit(_ name: String, _ grants: [String], _ at: Int) {
            frames[frames.count - 1].pending.append(Pending(atom: name, grants: grants, line: at))
        }
        while i < chars.count {
            let (a, name, at) = next()
            guard let atom = a else { emit(name, [], at)
             last = nil
             continue }
            if atom.declaration { head = true }
            if atom.exempt { exempt = true }
            if atom.foreign != nil {
                span(atom)
                 emit(name, atom.grants, at)
                 last = atom
                if let close = atom.foreign, byName[close]?.spelling == "\n" { lineHead = true }
                continue
            }
            if atom.medium { if atom.spelling == "\n" { lineHead = true }
             continue }
            let headsLine = lineHead
            if !atom.modifier { lineHead = false }
            if atom.opening {
                if atom.pairs {
                    frames.append(Frame(opener: name, context: exempt ? "Exempt" : ((last?.builder ?? false) || !head ? "Builder" : "Plain"), pending: []))
                    head = false
                     exempt = false
                } else { emit(name, atom.grants, at) }
                last = atom
                 continue
            }
            if let opening = atom.closes, frames.count > 1, frames.last?.opener == opening {
                finish(frames.removeLast())
                head = false
                exempt = false
                 last = atom
                 continue
            }
            if atom.line && !headsLine { emit("Midline<" + name + ">", [], at)
             last = atom
             continue }
            if atom.pair {
                var (other, otherName, _) = next()
                while other?.medium == true && i < chars.count { (other, otherName, _) = next() }
                lineHead = false
                let pairName = "Declares<" + name + ", " + otherName + ">"
                emit(pairName, pairs[pairName] ?? [], at)
                 last = other
                 continue
            }
            emit(name, atom.grants, at)
             last = atom
        }
        // An unfinished frame is flattened just as in the carried mirror.
        while frames.count > 1 {
            let frame = frames.removeLast()
            frames[frames.count - 1].pending += frame.pending
        }
        finish(frames[0])
        return bad.sorted { $0.line < $1.line }
    }
}
