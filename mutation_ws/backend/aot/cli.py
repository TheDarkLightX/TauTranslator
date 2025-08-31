import argparse
import json
import sys
from typing import List


def _safe_imports():
    cnl_parser = None
    tce_translator = None
    retrieve_top_k = None
    GrammarKnowledgePackBuilder = None
    try:
        from tau_translator_omega.core_engine.parsers.cnl_parser.parser import CNLParser  # type: ignore
        from tau_translator_omega.core_engine.translators.tce_tau_translator import (
            TCETauTranslator,  # type: ignore
        )
        cnl_parser = CNLParser
        tce_translator = TCETauTranslator
    except Exception:
        pass

    try:
        from backend.unified.domain.pack_retrieval import retrieve_top_k as _rtk  # type: ignore
        from backend.unified.domain.grammar_knowledge_pack import (
            GrammarKnowledgePackBuilder as _gkb,  # type: ignore
        )
        retrieve_top_k = _rtk
        GrammarKnowledgePackBuilder = _gkb
    except Exception:
        pass

    return cnl_parser, tce_translator, retrieve_top_k, GrammarKnowledgePackBuilder


def cmd_decompose(args: argparse.Namespace) -> int:
    problem = args.problem.strip()
    max_atoms = max(1, int(args.max_atoms))
    atoms: List[str] = [a.strip() for a in problem.replace("?", ".").split(".") if a.strip()]
    if not atoms:
        atoms = [problem]
    atoms = atoms[:max_atoms]
    print(json.dumps({"atoms": atoms}, ensure_ascii=False))
    return 0


def cmd_solve_atom(args: argparse.Namespace) -> int:
    # Stubbed solver; echoes atom with minimal transformation
    atom = args.atom.strip()
    mode = args.mode
    partial = atom
    confidence = 0.5 if mode == "assist" else 0.6
    print(json.dumps({"partial": partial, "confidence": confidence}, ensure_ascii=False))
    return 0


def _ensure_period(tce: str) -> str:
    tce = tce.strip()
    return tce if tce.endswith(".") else tce + "."


def cmd_tce_validate(args: argparse.Namespace) -> int:
    CNLParser, _, _, _ = _safe_imports()
    if CNLParser is None:
        print(json.dumps({"valid": False, "errors": ["CNLParser unavailable"]}))
        return 2
    tce = args.tce
    try:
        parser = CNLParser()
        parser.parse(_ensure_period(tce))
        print(json.dumps({"valid": True, "errors": []}))
        return 0
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"valid": False, "errors": [str(e)]}))
        return 1


def cmd_tce_to_tau(args: argparse.Namespace) -> int:
    CNLParser, TCETauTranslator, _, _ = _safe_imports()
    if CNLParser is None or TCETauTranslator is None:
        print(json.dumps({"success": False, "tau": None, "errors": ["Translator unavailable"]}))
        return 2
    tce = args.tce
    try:
        parser = CNLParser()
        ast = parser.parse(_ensure_period(tce))
        translator = TCETauTranslator()
        tau_result = translator.translate(ast)
        if getattr(tau_result, "errors", None):
            print(json.dumps({"success": False, "tau": None, "errors": tau_result.errors}))
            return 1
        tau_code = getattr(tau_result, "code", None)
        print(json.dumps({"success": True, "tau": tau_code, "errors": []}))
        return 0
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"success": False, "tau": None, "errors": [str(e)]}))
        return 1


def cmd_compose(args: argparse.Namespace) -> int:
    try:
        partials = json.loads(args.partials)
        if not isinstance(partials, list):
            raise ValueError("partials must be a JSON list of strings")
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"error": f"Invalid partials: {e}"}))
        return 2
    answer = " ".join([str(p).strip() for p in partials if str(p).strip()])
    print(json.dumps({"answer": answer}))
    return 0


def cmd_retrieve(args: argparse.Namespace) -> int:
    _, _, retrieve_top_k, GrammarKnowledgePackBuilder = _safe_imports()
    if retrieve_top_k is None or GrammarKnowledgePackBuilder is None:
        print(json.dumps({"items": [], "note": "Retrieval unavailable"}))
        return 2
    builder = GrammarKnowledgePackBuilder("data/grammar_packs")
    pack_res = builder.build_minimal(args.grammar_id, args.grammar_version)
    if getattr(pack_res, "is_failure", False) or getattr(pack_res, "__class__", None).__name__ == "Failure":
        print(json.dumps({"items": [], "note": "Pack build failed"}))
        return 1
    pack = pack_res.unwrap() if hasattr(pack_res, "unwrap") else pack_res
    top = retrieve_top_k(pack, args.query, k=int(args.k)).unwrap()
    print(json.dumps({"items": top}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tau-aot", description="Atom-of-Thoughts CLI for Tau Translator")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("decompose", help="Decompose a problem into atoms")
    sp.add_argument("--problem", required=True)
    sp.add_argument("--max-atoms", type=int, default=5)
    sp.set_defaults(func=cmd_decompose)

    sp = sub.add_parser("solve-atom", help="Solve a single atom (stub)")
    sp.add_argument("--atom", required=True)
    sp.add_argument("--mode", choices=["assist", "generate"], default="assist")
    sp.set_defaults(func=cmd_solve_atom)

    sp = sub.add_parser("compose", help="Compose partial answers")
    sp.add_argument("--partials", required=True, help="JSON list of strings")
    sp.set_defaults(func=cmd_compose)

    sp = sub.add_parser("tce-validate", help="Validate TCE using canonical parser")
    sp.add_argument("--tce", required=True)
    sp.set_defaults(func=cmd_tce_validate)

    sp = sub.add_parser("tce-to-tau", help="Translate TCE to Tau")
    sp.add_argument("--tce", required=True)
    sp.set_defaults(func=cmd_tce_to_tau)

    sp = sub.add_parser("retrieve", help="Retrieve top-k grammar knowledge items")
    sp.add_argument("--query", required=True)
    sp.add_argument("--k", type=int, default=5)
    sp.add_argument("--grammar-id", default="tce")
    sp.add_argument("--grammar-version", default="v1")
    sp.set_defaults(func=cmd_retrieve)

    return p


def main(argv: List[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())



