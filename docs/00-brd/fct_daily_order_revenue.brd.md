# Requirement: fct_daily_order_revenue

*SALES-2291, raised by Finance BI, 2026-08-28. Pasted verbatim.*

> **§1 Why.** Finance runs the daily trading call off a dashboard that today stitches three spreadsheets together. We need one governed table for daily revenue by region so the call and the regional sales review look at the same number.
>
> **§2 Sources.** Orders from the sales platform (`int_orders`). Region comes from the customer record in CRM (`dim_customer`).
>
> **§3 Shape.** A line per day per region, with how many orders and how much revenue.
>
> **§4 What counts.** Completed orders only. Revenue before tax.
>
> **§5 When.** Yesterday's numbers by 6am UTC.
>
> **§6 Who.** Finance BI and Sales Ops read it. Sales data engineering owns it.
