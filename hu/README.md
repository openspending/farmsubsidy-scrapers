Scraper for Hungary
=========================

<https://www.mvh.gov.hu/-/tamogatasi-adatok-a-bizottsag-908-2014-eu-vegrehajtasi-rendelete-alapjan-publication-of-data-according-to-commission-implementing-regulation-no-908-20>

Writing a scraper is painful (ASP viewstate).

Manually downloading CSV files from search by "Alap" and "Forrás" works though.
The individual files are stored in `data/` with the format `$ALAP-$FORRAS-$YEAR.csv`.
The provided Jupyter notebook combines these files and exports them into the necessary CSV.
