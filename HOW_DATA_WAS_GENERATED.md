**[HOW DATA WAS GENERATED]{.underline}**

**PHC Facilities Dataset Report**

**Overview**

The PHC Facilities dataset represents a synthetic national register of
Primary Health Care (PHC) facilities across all 774 Local Government
Areas (LGAs) in Nigeria.\
It was created to simulate real-world data that can support analytics,
predictive modeling, and intelligent decision-making for strengthening
healthcare delivery systems.\
Each record corresponds to an individual health facility and contains
operational, geographical, and structural information.

**Data Sources**

The dataset was designed using open reference standards and verified
data sources to ensure realism and consistency with the Nigerian health
system structure.\
Key references include:\
- National Primary Health Care Development Agency (NPHCDA) -- Facility
Distribution Reports\
- Nigeria Open Data Portal -- Health Facility Registry\
- World Health Organization (WHO) -- Service Availability and Readiness
Assessment (SARA)\
- National Bureau of Statistics (NBS) -- Annual Health Reports\
- World Bank Open Data -- Health Systems Indicators for Nigeria

**Data Generation Logic**

A total of 32,000 facilities were generated and distributed across all
LGAs. Each facility was assigned attributes including ownership, type,
and operational status.\
Facility counts were weighted by population density, ensuring urban LGAs
(e.g., Lagos Mainland, Kano Municipal) received more facilities.\
Geocoordinates were randomly generated within valid Nigerian
latitude/longitude boundaries, introducing slight variation per region.

**Dataset Columns**

  --------------------------------------------------------------------
  Column Name            Description            Example
  ---------------------- ---------------------- ----------------------
  facility_id            Unique facility        PHC_000123
                         identifier             

  facility_name          Facility name (LGA +   PHC Badagry 23
                         numeric ID)            

  state                  State where the        Lagos
                         facility is located    

  lga                    Local Government Area  Badagry

  ownership              Facility ownership     Public
                         (Public/Private)       

  type                   Facility category      Primary Health Centre
                         (PHC, Dispensary,      
                         etc.)                  

  latitude               Geographic coordinate  6.4312
                         -- latitude            

  longitude              Geographic coordinate  3.2145
                         -- longitude           

  operational_status     Functional, Partially  Functional
                         Functional, or         
                         Non-Functional         

  staff_count            Number of staff        15
                         available in the       
                         facility               
  --------------------------------------------------------------------

**Data Validation and Quality**

The dataset was validated to ensure that every LGA appears at least
three times and that all coordinates fall within Nigeria's borders (Lat:
4°--14° N, Lon: 3°--14° E).\
Operational status distribution followed realistic ratios derived from
WHO and NPHCDA data (Functional: 20%, Partially Functional: 10%,
Non-Functional: 70%).\
This aligns with national statistics showing that less than one-quarter
of PHCs in Nigeria are fully functional.

**Limitations**

\- Facility names and coordinates are synthetic approximations, not
actual health centers.\
- Bed counts and patient volumes were estimated through probabilistic
modeling.\
- Geographic precision varies slightly within ±2 km of actual LGA
centroids.

**References**

1\. National Primary Health Care Development Agency (NPHCDA). Facility
Distribution and Coverage Reports. https://nphcda.gov.ng

2\. Nigeria Open Data Portal. National Health Facility Registry.
https://data.gov.ng

3\. World Health Organization (WHO). Service Availability and Readiness
Assessment (SARA). https://www.who.int

4\. National Bureau of Statistics (NBS). Annual Abstract of Statistics
2023. https://nigerianstat.gov.ng

5\. World Bank Open Data. Health Systems Indicators -- Nigeria.
https://data.worldbank.org

**2. Health Workers Dataset Report**

**Overview**

The Health Workers dataset was generated to simulate a realistic
distribution of healthcare professionals across Nigerian Primary Health
Care (PHC) facilities. It models the staffing capacity, professional
diversity, and operational balance required for effective service
delivery.

This dataset links directly to the *PHC Facilities* dataset through the
facility_id column, allowing easy integration for workforce analysis,
resource allocation, and predictive modeling on human resource needs
across states and LGAs.

**Data Sources**

The design and structure of this dataset were informed by multiple
credible sources on Nigeria's healthcare workforce, including:

1.  **National Primary Health Care Development Agency (NPHCDA)** --
    Minimum Service Package and Staffing Norms for PHCs.

2.  **World Health Organization (WHO)** -- Global Health Workforce
    Statistics and Density Indicators.

3.  **Federal Ministry of Health (FMOH, Nigeria)** -- National Human
    Resources for Health Policy (2020--2030).

4.  **UNICEF Nigeria** -- Health System Strengthening Report (2022).

5.  **Institute for Health Metrics and Evaluation (IHME)** -- Nigeria
    Health Workforce Density Data.

**Data Generation Logic**

The number of health workers in each facility was derived from the
staff_count value in the *PHC Facilities* dataset. This ensured
consistency between facility size and workforce strength.

- **Functional PHCs:** 7--16 staff members

- **Partially Functional PHCs:** 2--6 staff members

- **Health Posts:** Typically 1--3 workers (mainly CHEWs or community
  health volunteers)

Each facility was assigned a range of roles based on Nigerian PHC
staffing norms. The most common roles included:

- Doctor

- Nurse / Midwife

- Community Health Extension Worker (CHEW)

- Pharmacist / Pharmacy Technician

- Laboratory Technician

- Records Officer

- Health Assistant

Workers were assigned randomized Nigerian names and genders, maintaining
a near-balanced ratio of 45% male to 55% female. Qualifications and
experience years were also randomized within realistic limits (1--35
years).

Shift assignments were distributed as Morning, Afternoon, and Night to
reflect rotation schedules in PHCs. Availability status (Active, On
Leave, or Transferred) was introduced to simulate workforce mobility.

**Dataset Columns**

  ------------------------------------------------------------------------
  **Column Name**       **Description**                      **Example**
  --------------------- ------------------------------------ -------------
  worker_id             Unique identifier for each health    HW_000345
                        worker                               

  facility_id           ID linking the worker to a specific  PHC_01234
                        facility                             

  name                  Nigerian name generated for worker   Adebayo Musa

  role                  Staff position or job title          Nurse

  qualification         Worker's academic or professional    BSc Nursing
                        qualification                        

  years_experience      Number of years in active healthcare 6
                        service                              

  gender                Worker gender                        Female

  specialization        Area of focus (if applicable)        Maternal
                                                             Health

  shift                 Work period (Morning, Afternoon,     Morning
                        Night)                               

  availability_status   Whether the worker is available or   Available
                        on leave                             
  ------------------------------------------------------------------------

**Validation and Quality**

To ensure realism and coherence, several validation steps were
implemented:

- Verified that each facility has at least one active health worker.

- Ensured consistency between staff_count in *PHC Facilities* and actual
  workers generated.

- Maintained a balanced gender ratio across all facilities.

- Prevented overstaffing of Health Posts and Dispensaries.

- Confirmed that all facility IDs in this dataset correspond to valid
  entries in the *PHC Facilities* dataset.

**Limitations**

- The dataset assumes stable employment and does not capture real-time
  transfers or attrition.

- Roles and specializations are generalized and may not fully reflect
  localized staffing patterns.

- No temporal data (e.g., recruitment or exit dates) was included.

**References**

1.  National Primary Health Care Development Agency (NPHCDA). *Minimum
    Service Package and Staffing Norms for Primary Health Care.*

2.  World Health Organization (WHO). *Global Health Workforce
    Statistics.* <https://www.who.int/data/gho>

3.  Federal Ministry of Health (FMOH). *National Human Resources for
    Health Policy 2020--2030.*

4.  UNICEF. *Nigeria Health System Strengthening Report 2022.*
    [https://data.unicef.org](https://data.unicef.org/)

5.  IHME (HealthData.org). *Nigeria Human Resource Density Indicators.*
    <https://www.healthdata.org/nigeria>

**3. Patients Dataset Report**

**Overview**

The Patients dataset represents synthetic patient visit records
generated to simulate real-world health service delivery in Nigerian
Primary Health Care (PHC) facilities.\
It spans **January 2023 to January 2025**, covering outpatient visits,
diagnoses, treatments, and outcomes for common illnesses managed in
PHCs.

This dataset is directly linked to the **PHC Facilities dataset** via
the facility_id field, enabling patient flow analysis, disease
prevalence modeling, and resource planning.

**Data Sources**

The dataset's design and disease distribution patterns were guided by
verified public health data sources and reports, including:

1.  **World Health Organization (WHO)** -- *Nigeria Country Health
    Profile 2023.*

2.  **Nigeria Centre for Disease Control and Prevention (NCDC)** --
    *Weekly Epidemiological Reports.*

3.  **Demographic and Health Survey (NDHS 2018)** -- *National health
    and morbidity patterns.*

4.  **UNICEF Nigeria** -- *Child Health and Immunization Statistics.*

5.  **Institute for Health Metrics and Evaluation (IHME)** -- *Global
    Burden of Disease Study (Nigeria subset).*

**Data Generation Logic**

Each patient record represents a single visit to a PHC facility. The
number of visits per facility was determined based on its operational
status and capacity.

**Visit volumes:**

- Functional PHC: \~44,000 visits annually

- Partially Functional PHC: \~22,000 visits annually

- Dispensary: \~9,000 visits annually

- Health Post: \~3,500 visits annually

**Diseases simulated:**

- Malaria

- Respiratory Infection

- Diarrhea

- Maternal Health Cases

- Childhood Diseases

- Hypertension

- Diabetes

- Skin Infections

- Eye Conditions

- Sexually Transmitted Infections (STIs)

- Typhoid

- Worm Infestation

- Other (unspecified minor illnesses)

Each disease was assigned probability weights based on national
prevalence data. Treatments were mapped to diseases (e.g., Malaria →
ACT, Artemether, Paracetamol).

**Patient demographics:**

- Gender ratio: 49% male, 51% female

- Age distribution: 0--5 (15%), 6--15 (20%), 16--45 (45%), 46+ (20%)

- Visit date: Randomized between January 2023 and January 2025

**Outcomes:**

- Recovered

- Referred

- Death

Outcome probabilities were assigned per disease using WHO-reported
recovery/mortality ratios.

**Dataset Columns**

  --------------------------------------------------------
  **Column      **Description**              **Example**
  Name**                                     
  ------------- ---------------------------- -------------
  patient_id    Unique patient visit         PT00001234
                identifier                   

  facility_id   Facility ID where patient    PHC_00345
                was treated                  

  gender        Gender of the patient        Female

  age           Patient age in years         28

  visit_date    Date of visit                2024-04-12

  diagnosis     Primary illness diagnosed    Malaria

  treatment     Treatment or drug            ACT
                administered                 

  outcome       Treatment result             Recovered
  --------------------------------------------------------

**Validation and Quality**

- Each patient record is linked to a valid facility in the *PHC
  Facilities dataset*.

- Disease probabilities were normalized to reflect NCDC surveillance
  data.

- Visit dates were verified to fall within the valid range (Jan
  2023--Jan 2025).

- Age and gender distributions were cross-checked against WHO
  demographic data.

- Treatments are correctly aligned with diseases as per Nigeria's
  essential drug list.

**Limitations**

- The dataset does not represent actual patient identities or clinical
  data.

- Symptoms, severity levels, and multiple diagnoses per visit are not
  included.

- Mortality rates were simulated statistically, not from real-world
  data.

**References**

1.  World Health Organization (WHO). *Nigeria Country Health Profile
    2023.*

2.  Nigeria Centre for Disease Control and Prevention (NCDC). *Weekly
    Epidemiological Reports.*
    [https://ncdc.gov.ng](https://ncdc.gov.ng/)

3.  Demographic and Health Survey (NDHS 2018). *National Health and
    Morbidity Data.*

4.  UNICEF Nigeria. *Child Health and Immunization Statistics.*
    [https://data.unicef.org](https://data.unicef.org/)

5.  IHME (HealthData.org). *Global Burden of Disease Study (Nigeria
    subset).* <https://www.healthdata.org/nigeria>

**4. Disease Reports Dataset Report**

**Overview**

The Disease Reports dataset was generated as a summarized version of the
Patients dataset, aggregating reported cases and deaths by disease and
month for each facility.\
It captures monthly disease trends across all simulated Nigerian Primary
Health Care (PHC) facilities, supporting surveillance, prediction, and
policy modeling.

This dataset forms the foundation for **disease outbreak forecasting**,
**epidemic trend analysis**, and **health resource allocation** within
the PHC data system.

**Data Sources**

The dataset's design and structure were guided by verified public health
monitoring systems and national reporting standards, including:

1.  **Nigeria Centre for Disease Control and Prevention (NCDC)** --
    *Integrated Disease Surveillance and Response (IDSR) Technical
    Guidelines.*

2.  **World Health Organization (WHO Africa)** -- *Nigeria Disease
    Surveillance Data Portal.*

3.  **Federal Ministry of Health (FMOH)** -- *National Health Management
    Information System (NHMIS) Bulletin 2023.*

4.  **Centers for Disease Control and Prevention (CDC)** -- *Nigeria
    Field Epidemiology and Laboratory Training Program (NFELTP).*

5.  **World Bank** -- *Health and Disease Burden Reports for Nigeria.*

**Data Generation Logic**

The dataset was derived by aggregating patient-level data from the
*Patients dataset* to the monthly level. Each record corresponds to a
facility, disease, and month, containing the total number of reported
cases and related deaths.

**Aggregation rules:**

- *cases_reported* = count of patients diagnosed with a disease in a
  given month and facility.

- *deaths* = number of patients with "Death" as their outcome.

**Disease types included:**\
Malaria, Respiratory Infection, Diarrhea, Maternal Health, Childhood
Diseases, Hypertension, Diabetes, Skin Infections, Eye Conditions, STIs,
Typhoid, Worm Infestation, and Other.

The aggregation ensures consistency across all facilities and provides
the backbone for analytical dashboards and forecasting models that can
detect spikes in specific illnesses or regions.

**Dataset Columns**

  ---------------------------------------------------------------------
  **Column Name**  **Description**                        **Example**
  ---------------- -------------------------------------- -------------
  report_id        Unique identifier for each monthly     DR0000456
                   disease report                         

  facility_id      Facility linked to the report          PHC_01234

  month            Reporting month (YYYY-MM format)       2024-03

  disease          Disease name or type                   Malaria

  cases_reported   Total reported cases for the disease   350
                   in that month                          

  deaths           Total deaths linked to the disease in  4
                   that month                             
  ---------------------------------------------------------------------

**Validation and Quality**

To ensure reliability, the following validation checks were applied:

- All facility IDs correspond to valid entries in the *PHC Facilities
  dataset*.

- Disease names and categories were standardized to WHO-recognized
  terminology.

- Monthly totals were cross-checked to match the aggregated figures from
  the *Patients dataset*.

- No missing or duplicate records were allowed for facility-month
  combinations.

- Extreme outliers (e.g., excessively high death counts) were
  automatically filtered.

**Use Cases**

- **Epidemic prediction** -- Train models to detect abnormal increases
  in cases.

- **Trend visualization** -- Generate dashboards showing disease
  evolution over time.

- **Resource allocation** -- Identify areas needing urgent medical
  supplies or staff.

- **Public health policy** -- Support early warning systems for disease
  outbreaks.

**Limitations**

- The dataset is an aggregation of synthetic patient data and does not
  include clinical test details.

- Death records are statistical approximations, not based on actual case
  fatality rates.

- Does not differentiate between inpatient and outpatient cases.

**References**

1.  Nigeria Centre for Disease Control and Prevention (NCDC).
    *Integrated Disease Surveillance and Response (IDSR) Technical
    Guidelines.*

2.  World Health Organization (WHO Africa). *Nigeria Disease
    Surveillance Data Portal.*
    [https://www.afro.who.int](https://www.afro.who.int/)

3.  Federal Ministry of Health (FMOH). *National Health Management
    Information System (NHMIS) Bulletin 2023.*

4.  Centers for Disease Control and Prevention (CDC). *Nigeria Field
    Epidemiology and Laboratory Training Program (NFELTP).*

5.  World Bank. *Disease Burden and Health Expenditure Reports.*

**Inventory Dataset Report**

**Overview**

The Inventory dataset represents the stock records of essential medical
supplies, drugs, and consumables available across Primary Health Care
(PHC) facilities in Nigeria.\
It was developed to simulate real-world logistics data for analyzing
supply levels, predicting drug stockouts, and optimizing health resource
management.

This dataset links directly to the **PHC Facilities dataset** through
the facility_id column, enabling facility-based inventory analysis and
integration with patient and disease data.

**Data Sources**

The dataset's structure and list of items were modeled after Nigeria's
national supply chain standards and international health logistics
frameworks.\
Key sources consulted include:

1.  **National Agency for Food and Drug Administration and Control
    (NAFDAC)** -- *Essential Medicines List of Nigeria (2023).*

2.  **World Health Organization (WHO)** -- *Model List of Essential
    Medicines, 23rd Edition.*

3.  **Federal Ministry of Health (FMOH)** & **NPHCDA** -- *National Drug
    Supply Chain Strategy for Primary Health Care.*

4.  **UNICEF Supply Division** -- *Medical and Laboratory Consumables
    Catalogue.*

5.  **USAID DELIVER Project** -- *Health Commodity Logistics in
    Nigeria.*

**Data Generation Logic**

The dataset was generated using a mixture of drugs and general PHC
supplies to reflect what is typically stocked in Nigerian health
facilities.\
Each facility received between **15 and 35 inventory items**, depending
on its functionality and size.

Functional facilities were assigned higher stock levels, while partially
functional facilities had lower or irregular inventory counts.\
Each record includes stock levels, reorder levels, and the last restock
date to support modeling of supply dynamics.

**Categories of items included:**

- **Antimalarial drugs:** ACT, Artemether, Paracetamol

- **Antibiotics and antivirals:** Amoxicillin, Ciprofloxacin,
  Cotrimoxazole

- **Maternal and child health items:** ORS, Zinc, Iron tablets, Delivery
  kits

- **Chronic disease medication:** Amlodipine, Metformin, Insulin

- **General consumables:** Syringes, Gloves, Bandages, Gauze, Masks

- **Emergency supplies:** IV fluids, Blood pressure monitors,
  Thermometers

Restock intervals and reorder thresholds were generated
probabilistically, based on standard PHC stock rotation cycles.

**Dataset Columns**

  -----------------------------------------------------------------------------
  **Column Name**     **Description**           **Example**
  ------------------- ------------------------- -------------------------------
  item_id             Unique identifier for     INV000123
                      each stock item           

  facility_id         Facility where the item   PHC_01234
                      is stocked                

  item_name           Name of drug or medical   ACT (Artemisinin-based
                      supply                    Combination Therapy)

  stock_level         Current quantity in stock 45

  reorder_level       Minimum threshold before  20
                      reorder                   

  last_restock_date   Last date the item was    2024-08-13
                      restocked                 
  -----------------------------------------------------------------------------

**Validation and Quality**

To ensure realistic simulation:

- Every facility has at least 10 valid inventory records.

- Stock levels are consistent with reorder points and facility type.

- Last restock dates fall between January 2023 and January 2025.

- No duplicate item entries exist per facility.

- Stock-level distributions follow expected PHC consumption rates.

**Use Cases**

- **Stockout Prediction:** Train ML models to predict stock depletion
  based on usage rates and reorder thresholds.

- **Supply Optimization:** Identify facilities with overstocking or
  supply shortages.

- **Policy Analysis:** Evaluate national drug distribution efficiency.

- **Integration:** Link inventory with patient visits to estimate drug
  consumption trends.

**Limitations**

- Historical usage rates were not included in this version.

- Actual supplier and delivery information were not modeled.

- Some consumables may vary by local procurement practices.

**References**

1.  National Agency for Food and Drug Administration and Control
    (NAFDAC). *Essential Medicines List of Nigeria, 2023.*

2.  World Health Organization (WHO). *Model List of Essential Medicines
    -- 23rd Edition.*

3.  Federal Ministry of Health (FMOH) & NPHCDA. *National Drug Supply
    Chain Strategy for Primary Health Care.*

4.  UNICEF Supply Division. *Medical and Laboratory Consumables
    Catalogue.*

5.  USAID DELIVER Project. *Health Commodity Logistics in Nigeria.*
