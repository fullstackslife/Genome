# Example Datasets

This directory contains synthetic example datasets for testing and demonstration.

## Files

- `example_bulk.csv` - Synthetic bulk RNA-seq data
  - Format: CSV with genes as rows, samples as columns
  - First column: Gene IDs
  - Remaining columns: Sample expression values
  - Size: 100 genes × 20 samples

- `example_single_cell.h5ad` - Synthetic single-cell RNA-seq data
  - Format: AnnData (.h5ad)
  - Contains expression matrix and minimal metadata
  - Size: 100 genes × 50 cells

## Generating Examples

Run the generation script:

```bash
python data/examples/generate_examples.py
```

This will create the example files in this directory.

## Data Format

### Bulk RNA-seq (CSV)

```
GENE_ID,SAMPLE_000,SAMPLE_001,SAMPLE_002,...
GENE_00000,123.45,234.56,345.67,...
GENE_00001,234.56,345.67,456.78,...
...
```

### Single-cell RNA-seq (.h5ad)

AnnData format with:
- `X`: Expression matrix (cells × genes)
- `obs`: Cell metadata (non-identifying)
- `var`: Gene metadata

## Usage

These examples can be ingested via the API:

```bash
# Bulk RNA-seq
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@data/examples/example_bulk.csv"

# Single-cell
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@data/examples/example_single_cell.h5ad"
```

## Note

These are **synthetic datasets** for testing only. They do not represent real biological data and should not be used for any biological analysis.
