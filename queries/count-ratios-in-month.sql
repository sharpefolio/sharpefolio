SELECT COUNT(*)
FROM ratios
WHERE
	`date` >= '2014-04-01' AND
	`date` <  '2014-05-01';

#SELECT `date` FROM ratios ORDER BY `date` DESC LIMIT 10;