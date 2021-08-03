--death per cases
SELECT location, date, total_cases, total_deaths, (total_deaths/total_cases)*100 AS percentage_death
  FROM [Portofolio].[dbo].covidDeaths
  WHERE location like '%indonesia' and continent is not null
  ORDER BY 2

--cases per population
  SELECT location, date, population, total_cases, (total_cases/population)*100 AS percentage_cases
  FROM [Portofolio].[dbo].covidDeaths
  WHERE location like '%indonesia' and continent is not null
  ORDER BY 2

  --highest infection in the world
  SELECT location, population, MAX(total_cases) as Infection, MAX((cast(total_cases as float)/cast(population as float)))*100 AS percentage_population_infected
  FROM [Portofolio].[dbo].covidDeaths
  GROUP BY location, population
  ORDER BY 4 DESC

  --highest deaths country
  SELECT location, MAX(cast(total_deaths as int)) as total_deaths, MAX((cast(total_deaths as float)/population))*100 AS percentage_population_deaths
  FROM [Portofolio].[dbo].covidDeaths
  where continent is not null
  GROUP BY location
  ORDER BY 2 DESC

  --highest by continent
  SELECT continent, MAX(cast(total_deaths as int)) as total_deaths, MAX((cast(total_deaths as float)/population))*100 AS percentage_population_deaths
  FROM [Portofolio].[dbo].covidDeaths
  where continent is not null
  GROUP BY continent
  ORDER BY 2 DESC

--Global Number 
SELECT location, date, total_cases, total_deaths, (total_deaths/total_cases)*100 AS percentage_death
  FROM [Portofolio].[dbo].covidDeaths
  WHERE continent is not null
  ORDER BY 4 DESC

--Population vs Vaccinations
--CTE
WITH VaccPerPop (Continent, Location, Date, Population, New_Vaccinations, Total_Vaccinations)
as
(
SELECT dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, 
	SUM(cast(vac.new_vaccinations as int)) OVER (PARTITION BY dea.location ORDER BY dea.location, dea.date) as
	Total_Vaccinations
From Portofolio..covidDeaths dea
JOIN Portofolio..covidVaccinations vac
	ON dea.date = vac.date
	and dea.location = vac.location
WHERE dea.continent is not null
)

SELECT *, (Total_Vaccinations/Population)*100 as Vaccination_Percentage
FROM VaccPerPop




--TEMP TABLE
DROP TABLE IF exists #PopulationVaccinated
CREATE TABLE #PopulationVaccinated
(Continent nvarchar(100),
Location nvarchar(100),
Date datetime,
Population numeric,
New_Vaccinations numeric,
Total_Vaccinations numeric)

INSERT INTO #PopulationVaccinated
SELECT dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, 
	SUM(CONVERT(int, vac.new_vaccinations)) OVER (PARTITION BY dea.location ORDER BY dea.location, dea.date) as
	Total_Vaccinations
From Portofolio..covidDeaths dea
JOIN Portofolio..covidVaccinations vac
	ON dea.date = vac.date
	and dea.location = vac.location
WHERE dea.continent is not null

SELECT *, (Total_Vaccinations/Population)*100 as Vaccination_Percentage
FROM #PopulationVaccinated


--VIEW
CREATE VIEW PopulationVaccinated as
SELECT dea.continent, dea.location, dea.date, dea.population, vac.new_vaccinations, 
	SUM(CONVERT(int, vac.new_vaccinations)) OVER (PARTITION BY dea.location ORDER BY dea.location, dea.date) as
	Total_Vaccinations
From Portofolio..covidDeaths dea
JOIN Portofolio..covidVaccinations vac
	ON dea.date = vac.date
	and dea.location = vac.location
WHERE dea.continent is not null

SELECT *
FROM Portofolio..PopulationVaccinated