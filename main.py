#!/usr/bin/env python3
"""
CLI Entry point for the AI Resume Screening & Ranking System.
Usage:
    python3 main.py --input ./resumes --output ./output/results.json
"""
import os
import sys
import json
import logging
import argparse
from typing import List, Dict, Any

from src.pipeline import run_screening_pipeline
from src.models.schemas import ScreeningOutput

def render_terminal_table(output: ScreeningOutput):
    """Print clean formatted summary table to stdout."""
    summary = output.summary
    print("\n" + "=" * 80)
    print(" 🚀 AI RESUME SCREENING & RANKING SYSTEM — BATCH REPORT")
    print("=" * 80)
    print(f" Total Resumes Processed : {summary.total_resumes}")
    print(f" Successfully Parsed     : {summary.successfully_parsed}")
    print(f" Eligible Candidates     : {summary.eligible}")
    print(f" Rejected Candidates     : {summary.rejected}")
    print(f" Unreadable / Malformed  : {summary.failed_unreadable}")
    print(f" Execution Time          : {summary.execution_time_seconds:.2f} seconds")
    print("-" * 80)

    print("\n🏆 RANKED SHORTLIST (ELIGIBLE CANDIDATES):")
    if not output.ranked_candidates:
        print("  (No eligible candidates found in batch)")
    else:
        print(f"{'Rank':<5} {'Candidate Name':<22} {'Score':<8} {'AI':<6} {'Python':<8} {'Cloud':<7} {'GH':<5} {'Eng':<5} {'Matched Skills'}")
        print("-" * 95)
        for c in output.ranked_candidates:
            b = c.score_breakdown
            skills_str = ", ".join(c.matched_skills[:4])
            print(f"#{c.rank:<4} {c.candidate_name[:20]:<22} {c.total_score:<8.1f} {b.ai_project_depth:<6.1f} {b.python_backend:<8.1f} {b.cloud_fullstack:<7.1f} {b.github:<5.1f} {b.engineering_depth:<5.1f} {skills_str}")

    if output.rejected_candidates:
        print("\n❌ REJECTED CANDIDATES (HARD FILTER / MALFORMED):")
        print(f"{'Candidate Name':<25} {'Rejection Reasons'}")
        print("-" * 80)
        for c in output.rejected_candidates:
            reasons = "; ".join(c.rejection_reasons)
            print(f"{c.candidate_name[:23]:<25} {reasons}")

    print("\n" + "=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="AI Resume Screening & Ranking System")
    parser.add_argument("--input", "-i", default="./resumes", help="Directory path containing resumes (PDF/DOCX/TXT)")
    parser.add_argument("--output", "-o", default="./output/results.json", help="Output JSON file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logging")
    args = parser.parse_args()

    # Set clean log level unless verbose is explicitly enabled
    if not args.verbose:
        logging.getLogger("ResumeScreener").setLevel(logging.ERROR)
        logging.getLogger().setLevel(logging.ERROR)

    input_dir = os.path.abspath(args.input)
    output_file = os.path.abspath(args.output)

    if not os.path.exists(input_dir):
        print(f"Error: Input directory does not exist: {input_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Screening resumes in '{os.path.basename(input_dir)}' directory...")
    screening_output = run_screening_pipeline(input_dir)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    export_data = {
        "batch_summary": screening_output.summary.model_dump(),
        "ranked_candidates": [c.model_dump(exclude_none=True) for c in screening_output.ranked_candidates],
        "rejected_candidates": [c.model_dump(exclude_none=True) for c in screening_output.rejected_candidates]
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2)

    render_terminal_table(screening_output)
    print(f"💾 Full results saved successfully to: {output_file}")


if __name__ == "__main__":
    main()
