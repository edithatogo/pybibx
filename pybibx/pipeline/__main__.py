from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import NoReturn

from pybibx.pipeline.providers import (
    PipelineError,
    PipelineOutputFormat,
    ProviderPipelineRequest,
    export_provider_pipeline_result,
    run_provider_pipeline,
)
from pybibx.schemas import ProviderName


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the offline PyBibX provider pipeline.")
    parser.add_argument("--provider", action="append", required=True, help="Provider name, repeated per input.")
    parser.add_argument("--input", action="append", required=True, help="Local input path, repeated per provider.")
    parser.add_argument(
        "--output-format",
        choices=[item.value for item in PipelineOutputFormat],
        default=PipelineOutputFormat.JSONL.value,
    )
    parser.add_argument("--output", type=Path, required=True, help="Output file path.")
    parser.add_argument("--allow-credential-gated", action="store_true")
    parser.add_argument("--allow-export-import-only", action="store_true")
    args = parser.parse_args()

    if len(args.provider) != len(args.input):
        _die("--provider and --input must be supplied the same number of times")

    inputs = {ProviderName(provider): Path(path) for provider, path in zip(args.provider, args.input, strict=True)}
    request = ProviderPipelineRequest(
        inputs=inputs,
        output_format=PipelineOutputFormat(args.output_format),
        allow_credential_gated=args.allow_credential_gated,
        allow_export_import_only=args.allow_export_import_only,
    )
    try:
        result = run_provider_pipeline(request)
        export_provider_pipeline_result(result, args.output, request.output_format)
    except PipelineError as exc:
        _die(str(exc))
    sys.stdout.write(f"Wrote {len(result.works)} works to {args.output}\n")


def _die(message: str) -> NoReturn:
    raise SystemExit(message)


if __name__ == "__main__":
    main()
