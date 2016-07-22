SELECT 
a.date, 
b.market, 
a.market, 
b.ask, 
a.bid, 
a.bid-b.ask AS diff, 
b.ask_amount, 
a.bid_amount, 
ROUND(least(b.ask_amount, a.bid_amount),5) as amount,
ROUND((a.bid-b.ask) * least(b.ask_amount, a.bid_amount)) as potential_profit
FROM prices AS a
JOIN (
SELECT *
FROM prices
WHERE market='bithumb' AND seq=1
	) b ON a.date = b.date AND a.market <> b.market AND (a.bid > b.ask)
WHERE a.market='korbit' AND a.seq=1
;
