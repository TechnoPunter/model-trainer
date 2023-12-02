update scrip_hist
set
  hour = extract(HOUR from (TIMESTAMP 'epoch' + time * interval '1 second') AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata'),
  minute = extract(MINUTE FROM (TIMESTAMP 'epoch' + time * interval '1 second') AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Kolkata')
WHERE
  hour IS NULL AND minute IS NULL;


delete from scrip_hist where hour = 9 and minute <=14;

