SELECT 
  c.CustomerKey, 
  c.firstname AS FirstName, 
  c.lastname AS LastName, 
  c.FirstName + ' ' + c.LastName AS FullName, 
  CASE c.Gender WHEN 'M' THEN 'Male' WHEN 'F' THEN 'Female' END AS Gender,
  c.datefirstpurchase AS DateFirstPurchase,
  g.City AS CustomerCity 
FROM 
  [AdventureWorksDW2019].[dbo].[DimCustomer] c 
  LEFT JOIN [AdventureWorksDW2019].[dbo].[DimGeography] g ON c.GeographyKey = g.GeographyKey 
ORDER BY 
  1 ASC