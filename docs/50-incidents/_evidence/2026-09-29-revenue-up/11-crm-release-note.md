# #crm-platform-announcements · 2026-09-25 17:02 UTC

**CRM platform team:** Heads up: tonight we're releasing **dim_customer v2.0**. It's now SCD Type 2, so region and segment changes are kept as history (`valid_from`, `valid_to`, `is_current`). If you only want the current record, filter `is_current = true`. Contract updated in the crm-platform repo (`docs/10-contract/dim_customer.contract.md` → 2.0).
