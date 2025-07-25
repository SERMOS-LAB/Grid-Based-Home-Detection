.. GHOST documentation master file, created by sphinx-quickstart

Welcome to GHOST's documentation!
=================================

GHOST: Grid-based Home detection via Stay-Time
==============================================

A modular, open-source Python package for detecting home locations from mobile GPS data using the GHOST algorithm (Grid-based Home detection via Stay-Time). Designed for urban data science research, reproducibility, and open science best practices.

Features
--------
- GHOST algorithm: grid-based home detection with nighttime and weekend fallback
- Stay-time calculation
- Batch and single-user support
- Flexible config and CLI
- Extensible for benchmarking (DBSCAN, KMeans++)
- Publication-ready documentation and validation

Batch Processing and Validation
-------------------------------
- Batch mode is triggered automatically when your input is a folder of GPX files (one per user) or a CSV with a user_id column.
- The CLI and Python API output one row per user with all stats (lat, lon, stay_time, inferred_from, etc.).
- The validate command prints per-user errors (in meters) and a summary of batch accuracy metrics when multiple users are present.
- For single-user, all commands work as expected.

Quickstart
----------
.. code-block:: python

    from ghost.detector import HomeDetector  # GHOST high-level API
    detector = HomeDetector(input_file='data.gpx')
    detector.load_data().preprocess_data().detect_homes()
    results = detector.get_results()
    print(results)

API Reference
-------------
.. automodule:: ghost.detector
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: ghost.algorithms.grid
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: ghost.preprocessing.projection
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: ghost.preprocessing.time
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: ghost.io.gpx
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: ghost.utils
    :members:
    :undoc-members:
    :show-inheritance:

Citation
--------
If you use GHOST in your research, please cite:

.. code-block:: bibtex

    @misc{recalde2025ghost,
      author = {Alessandra Recalde and Mustafa Sameen and Xiaojian Zhang and Xilei Zhao},
      title = {DESIGN AND VALIDATION OF A GRID-BASED HOME DETECTION VIA STAY-TIME (GHOST) SOFTWARE FOR MOBILE LOCATION DATA},
      year = {2025},
      note = {University of Florida},
      howpublished = {\url{https://github.com/SERMOS-LAB/Grid-Based-Home-Detection}},
      institution = {University of Florida},
      address = {Gainesville, Florida, 32611}
    }


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`