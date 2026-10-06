# Probe results

*What the investigator would query next. Simulated results, consistent with the rest of the pack.*

## P1: Is dim_customer still one row per customer_id? (J-01 assumes N:1)

```sql
SELECT count(*) AS rows, count(DISTINCT customer_id) AS customers,
       count_if(is_current) AS current_rows
FROM prod.crm_silver.dim_customer;
```
| rows | customers | current_rows |
|---|---|---|
| 61,483 | 48,402 | 48,402 |

## P2: Control totals: fact vs source, by day (EMEA)

```sql
-- completed, non-test revenue straight from int_orders vs the published fact
```
| order_date | source_revenue_cents | fact_revenue_cents | ratio | source_orders | fact_completed_order_count |
|---|---|---|---|---|---|
| 2026-09-21 | 33,410,200 | 33,410,200 | 1.00 | 2,904 | 2,904 |
| 2026-09-22 | 33,105,900 | 33,105,900 | 1.00 | 2,877 | 2,877 |
| 2026-09-23 | 33,688,100 | 40,425,720 | 1.20 | 2,931 | 2,931 |
| 2026-09-24 | 33,201,450 | 39,841,740 | 1.20 | 2,890 | 2,890 |
| 2026-09-25 | 33,425,700 | 40,112,800 | 1.20 | 2,911 | 2,911 |
| 2026-09-26 | 33,906,100 | 41,027,350 | 1.21 | 2,948 | 2,948 |
| 2026-09-27 | 33,233,700 | 39,880,410 | 1.20 | 2,887 | 2,887 |
| 2026-09-28 | 33,324,500 | 40,655,900 | 1.22 | 2,902 | 2,902 |

## P3: int_orders: duplicate or late loads?

```sql
SELECT order_date, count(*) AS rows, count(DISTINCT order_id) AS orders FROM prod.sales_silver.int_orders
WHERE order_date BETWEEN '2026-09-21' AND '2026-09-28' GROUP BY 1;
```
rows = orders on every day. No duplicates. `DESCRIBE HISTORY` on int_orders shows the normal nightly MERGE only.
