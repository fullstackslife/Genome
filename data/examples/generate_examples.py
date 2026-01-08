"""Generate synthetic example datasets for testing."""

import numpy as np
import pandas as pd
from pathlib import Path

# For single-cell example
try:
    import anndata as ad
    HAS_ANNDATA = True
except ImportError:
    HAS_ANNDATA = False


def generate_bulk_example(output_path: Path, num_genes: int = 100, num_samples: int = 20):
    """
    Generate synthetic bulk RNA-seq example data.

    Args:
        output_path: Path to save CSV file
        num_genes: Number of genes
        num_samples: Number of samples
    """
    # Set random seed for reproducibility
    np.random.seed(42)

    # Generate gene names
    gene_ids = [f"GENE_{i:05d}" for i in range(num_genes)]

    # Generate sample names
    sample_ids = [f"SAMPLE_{i:03d}" for i in range(num_samples)]

    # Generate expression values (log-normal distribution)
    # Simulate realistic RNA-seq counts
    base_expression = np.random.lognormal(mean=5, sigma=2, size=(num_genes, num_samples))
    
    # Add some structure: some genes vary more between samples
    for i in range(num_genes // 10):
        sample_variation = np.random.normal(0, 1, num_samples)
        base_expression[i, :] += sample_variation * 2

    # Create DataFrame
    df = pd.DataFrame(
        base_expression,
        index=gene_ids,
        columns=sample_ids,
    )

    # Save to CSV
    df.to_csv(output_path, index=True)
    print(f"Generated bulk RNA-seq example: {output_path}")
    print(f"  Genes: {num_genes}, Samples: {num_samples}")


def generate_single_cell_example(output_path: Path, num_genes: int = 100, num_cells: int = 50):
    """
    Generate synthetic single-cell RNA-seq example data (.h5ad).

    Args:
        output_path: Path to save .h5ad file
        num_genes: Number of genes
        num_cells: Number of cells
    """
    if not HAS_ANNDATA:
        print("Warning: anndata not available, skipping single-cell example")
        return

    # Set random seed for reproducibility
    np.random.seed(42)

    # Generate gene names
    gene_ids = [f"GENE_{i:05d}" for i in range(num_genes)]

    # Generate cell names
    cell_ids = [f"CELL_{i:04d}" for i in range(num_cells)]

    # Generate expression matrix (sparse-like, many zeros)
    # Single-cell data is typically sparse
    expression = np.random.negative_binomial(n=5, p=0.3, size=(num_cells, num_genes))
    
    # Make it sparse (many zeros)
    mask = np.random.random((num_cells, num_genes)) > 0.7
    expression[mask] = 0

    # Create AnnData object
    adata = ad.AnnData(X=expression.astype(np.float32))

    # Set gene and cell names
    adata.var_names = gene_ids
    adata.obs_names = cell_ids

    # Add some minimal metadata (non-identifying)
    adata.obs["n_genes"] = (expression > 0).sum(axis=1)
    adata.obs["total_counts"] = expression.sum(axis=1)
    adata.obs["batch"] = np.random.choice(["batch_A", "batch_B"], size=num_cells)

    # Save
    adata.write_h5ad(output_path)
    print(f"Generated single-cell example: {output_path}")
    print(f"  Genes: {num_genes}, Cells: {num_cells}")


if __name__ == "__main__":
    examples_dir = Path(__file__).parent
    examples_dir.mkdir(parents=True, exist_ok=True)

    # Generate bulk example
    bulk_path = examples_dir / "example_bulk.csv"
    generate_bulk_example(bulk_path, num_genes=100, num_samples=20)

    # Generate single-cell example
    if HAS_ANNDATA:
        sc_path = examples_dir / "example_single_cell.h5ad"
        generate_single_cell_example(sc_path, num_genes=100, num_cells=50)
    else:
        print("Skipping single-cell example (anndata not installed)")
