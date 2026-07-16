# Data Dictionary

Every CSV column is profiled below using actual loaded files.

## charging_load

| column                            | dtype   |   non_null |   nulls |   unique_values |       min |       max | meaning                                                                 |
|:----------------------------------|:--------|-----------:|--------:|----------------:|----------:|----------:|:------------------------------------------------------------------------|
| time_slot                         | int64   |        289 |       0 |             289 |    0      |   288     | Temporal index or time-of-day field from the aggregated public dataset. |
| Private car_P1_workday            | float64 |        289 |       0 |             288 | 1067.41   |  4464.01  | Charging power-level or delivered-power aggregate/statistic.            |
| Private car_P2_workday            | float64 |        289 |       0 |             288 | 1982.49   | 14893.8   | Charging power-level or delivered-power aggregate/statistic.            |
| Private car_P3_workday            | float64 |        289 |       0 |             288 |  972.041  |  7597.22  | Charging power-level or delivered-power aggregate/statistic.            |
| Taxi_P1_workday                   | float64 |        289 |       0 |             288 |   30.5597 |   210.992 | Charging power-level or delivered-power aggregate/statistic.            |
| Taxi_P2_workday                   | float64 |        289 |       0 |             288 |  202.774  |  2649.81  | Charging power-level or delivered-power aggregate/statistic.            |
| Taxi_P3_workday                   | float64 |        289 |       0 |             288 |  311.021  |  1862.8   | Charging power-level or delivered-power aggregate/statistic.            |
| Official car_P1_workday           | float64 |        289 |       0 |             288 |  187.468  |   552.054 | Charging power-level or delivered-power aggregate/statistic.            |
| Official car_P2_workday           | float64 |        289 |       0 |             288 |  690.407  |  3354.43  | Charging power-level or delivered-power aggregate/statistic.            |
| Official car_P3_workday           | float64 |        289 |       0 |             288 | 1264.12   |  5427.72  | Charging power-level or delivered-power aggregate/statistic.            |
| Rental car_P1_workday             | float64 |        289 |       0 |             288 |   47.8646 |   144.849 | Charging power-level or delivered-power aggregate/statistic.            |
| Rental car_P2_workday             | float64 |        289 |       0 |             288 |  150.809  |   644.571 | Charging power-level or delivered-power aggregate/statistic.            |
| Rental car_P3_workday             | float64 |        289 |       0 |             288 |  586.463  |  4643.19  | Charging power-level or delivered-power aggregate/statistic.            |
| Bus_P1_workday                    | float64 |        289 |       0 |             288 | 1998.42   | 16658     | Charging power-level or delivered-power aggregate/statistic.            |
| Bus_P2_workday                    | float64 |        289 |       0 |             288 | 3835.92   | 24150.3   | Charging power-level or delivered-power aggregate/statistic.            |
| Bus_P3_workday                    | float64 |        289 |       0 |             288 | 3475.27   | 61999.2   | Charging power-level or delivered-power aggregate/statistic.            |
| SPV_P1_workday                    | float64 |        289 |       0 |             288 |  172.915  |   764.039 | Charging power-level or delivered-power aggregate/statistic.            |
| SPV_P2_workday                    | float64 |        289 |       0 |             288 | 1559.12   |  8714.12  | Charging power-level or delivered-power aggregate/statistic.            |
| SPV_P3_workday                    | float64 |        289 |       0 |             288 |  446.537  |  1596.39  | Charging power-level or delivered-power aggregate/statistic.            |
| Private car_P1_weekend & holiday  | float64 |        289 |       0 |             288 | 1072.22   |  4252.61  | Charging power-level or delivered-power aggregate/statistic.            |
| Private car_P2_weekend & holiday  | float64 |        289 |       0 |             288 | 2062.58   | 16238     | Charging power-level or delivered-power aggregate/statistic.            |
| Private car_P3_weekend & holiday  | float64 |        289 |       0 |             288 | 1176.79   |  7992.72  | Charging power-level or delivered-power aggregate/statistic.            |
| Taxi_P1_weekend & holiday         | float64 |        289 |       0 |             288 |   34.0395 |   245.271 | Charging power-level or delivered-power aggregate/statistic.            |
| Taxi_P2_weekend & holiday         | float64 |        289 |       0 |             288 |  286.925  |  2803.22  | Charging power-level or delivered-power aggregate/statistic.            |
| Taxi_P3_weekend & holiday         | float64 |        289 |       0 |             288 |  381.069  |  1626.07  | Charging power-level or delivered-power aggregate/statistic.            |
| Official car_P1_weekend & holiday | float64 |        289 |       0 |             288 |  171.175  |   615.126 | Charging power-level or delivered-power aggregate/statistic.            |
| Official car_P2_weekend & holiday | float64 |        289 |       0 |             288 |  789.717  |  3791.84  | Charging power-level or delivered-power aggregate/statistic.            |
| Official car_P3_weekend & holiday | float64 |        289 |       0 |             288 | 1548.66   |  5885.37  | Charging power-level or delivered-power aggregate/statistic.            |
| Rental car_P1_weekend & holiday   | float64 |        289 |       0 |             288 |   60.6366 |   187.52  | Charging power-level or delivered-power aggregate/statistic.            |
| Rental car_P2_weekend & holiday   | float64 |        289 |       0 |             288 |  196.812  |   823.473 | Charging power-level or delivered-power aggregate/statistic.            |
| Rental car_P3_weekend & holiday   | float64 |        289 |       0 |             288 |  873.202  |  5813.56  | Charging power-level or delivered-power aggregate/statistic.            |
| Bus_P1_weekend & holiday          | float64 |        289 |       0 |             288 | 2214.65   | 21264.5   | Charging power-level or delivered-power aggregate/statistic.            |
| Bus_P2_weekend & holiday          | float64 |        289 |       0 |             288 | 3679.49   | 18607.1   | Charging power-level or delivered-power aggregate/statistic.            |
| Bus_P3_weekend & holiday          | float64 |        289 |       0 |             288 | 3875.21   | 45513.1   | Charging power-level or delivered-power aggregate/statistic.            |
| SPV_P1_weekend & holiday          | float64 |        289 |       0 |             288 |  182.818  |   881.13  | Charging power-level or delivered-power aggregate/statistic.            |
| SPV_P2_weekend & holiday          | float64 |        289 |       0 |             288 | 1728.49   | 10848.2   | Charging power-level or delivered-power aggregate/statistic.            |
| SPV_P3_weekend & holiday          | float64 |        289 |       0 |             288 |  433.25   |  1864.63  | Charging power-level or delivered-power aggregate/statistic.            |

## vehicle_count

| column                            | dtype   |   non_null |   nulls |   unique_values |   min |   max | meaning                                                                 |
|:----------------------------------|:--------|-----------:|--------:|----------------:|------:|------:|:------------------------------------------------------------------------|
| time_slot                         | int64   |        289 |       0 |             289 |     0 |   288 | Temporal index or time-of-day field from the aggregated public dataset. |
| Private car_P1_workday            | int64   |        289 |       0 |             229 |   400 |  1331 | Charging power-level or delivered-power aggregate/statistic.            |
| Private car_P2_workday            | int64   |        289 |       0 |             255 |   348 |  2551 | Charging power-level or delivered-power aggregate/statistic.            |
| Private car_P3_workday            | int64   |        289 |       0 |             143 |    38 |   270 | Charging power-level or delivered-power aggregate/statistic.            |
| Taxi_P1_workday                   | int64   |        289 |       0 |              59 |    11 |    69 | Charging power-level or delivered-power aggregate/statistic.            |
| Taxi_P2_workday                   | int64   |        289 |       0 |             184 |    33 |   427 | Charging power-level or delivered-power aggregate/statistic.            |
| Taxi_P3_workday                   | int64   |        289 |       0 |              51 |    14 |    75 | Charging power-level or delivered-power aggregate/statistic.            |
| Official car_P1_workday           | int64   |        289 |       0 |             106 |    70 |   194 | Charging power-level or delivered-power aggregate/statistic.            |
| Official car_P2_workday           | int64   |        289 |       0 |             186 |   115 |   559 | Charging power-level or delivered-power aggregate/statistic.            |
| Official car_P3_workday           | int64   |        289 |       0 |             124 |    70 |   230 | Charging power-level or delivered-power aggregate/statistic.            |
| Rental car_P1_workday             | int64   |        289 |       0 |              34 |    18 |    51 | Charging power-level or delivered-power aggregate/statistic.            |
| Rental car_P2_workday             | int64   |        289 |       0 |              75 |    24 |    99 | Charging power-level or delivered-power aggregate/statistic.            |
| Rental car_P3_workday             | int64   |        289 |       0 |             107 |    26 |   176 | Charging power-level or delivered-power aggregate/statistic.            |
| Bus_P1_workday                    | int64   |        289 |       0 |             171 |    75 |   562 | Charging power-level or delivered-power aggregate/statistic.            |
| Bus_P2_workday                    | int64   |        289 |       0 |             157 |    67 |   311 | Charging power-level or delivered-power aggregate/statistic.            |
| Bus_P3_workday                    | int64   |        289 |       0 |             157 |    37 |   361 | Charging power-level or delivered-power aggregate/statistic.            |
| SPV_P1_workday                    | int64   |        289 |       0 |             121 |    43 |   177 | Charging power-level or delivered-power aggregate/statistic.            |
| SPV_P2_workday                    | int64   |        289 |       0 |             156 |    59 |   315 | Charging power-level or delivered-power aggregate/statistic.            |
| SPV_P3_workday                    | int64   |        289 |       0 |              20 |     7 |    26 | Charging power-level or delivered-power aggregate/statistic.            |
| Private car_P1_weekend & holiday  | int64   |        289 |       0 |             244 |   413 |  1518 | Charging power-level or delivered-power aggregate/statistic.            |
| Private car_P2_weekend & holiday  | int64   |        289 |       0 |             266 |   365 |  2812 | Charging power-level or delivered-power aggregate/statistic.            |
| Private car_P3_weekend & holiday  | int64   |        289 |       0 |             151 |    48 |   289 | Charging power-level or delivered-power aggregate/statistic.            |
| Taxi_P1_weekend & holiday         | int64   |        289 |       0 |              70 |    12 |    81 | Charging power-level or delivered-power aggregate/statistic.            |
| Taxi_P2_weekend & holiday         | int64   |        289 |       0 |             189 |    47 |   455 | Charging power-level or delivered-power aggregate/statistic.            |
| Taxi_P3_weekend & holiday         | int64   |        289 |       0 |              46 |    18 |    68 | Charging power-level or delivered-power aggregate/statistic.            |
| Official car_P1_weekend & holiday | int64   |        289 |       0 |             124 |    72 |   225 | Charging power-level or delivered-power aggregate/statistic.            |
| Official car_P2_weekend & holiday | int64   |        289 |       0 |             191 |   143 |   643 | Charging power-level or delivered-power aggregate/statistic.            |
| Official car_P3_weekend & holiday | int64   |        289 |       0 |             123 |    91 |   260 | Charging power-level or delivered-power aggregate/statistic.            |
| Rental car_P1_weekend & holiday   | int64   |        289 |       0 |              46 |    21 |    66 | Charging power-level or delivered-power aggregate/statistic.            |
| Rental car_P2_weekend & holiday   | int64   |        289 |       0 |              90 |    29 |   123 | Charging power-level or delivered-power aggregate/statistic.            |
| Rental car_P3_weekend & holiday   | int64   |        289 |       0 |             119 |    39 |   221 | Charging power-level or delivered-power aggregate/statistic.            |
| Bus_P1_weekend & holiday          | int64   |        289 |       0 |             166 |    79 |   717 | Charging power-level or delivered-power aggregate/statistic.            |
| Bus_P2_weekend & holiday          | int64   |        289 |       0 |             143 |    63 |   304 | Charging power-level or delivered-power aggregate/statistic.            |
| Bus_P3_weekend & holiday          | int64   |        289 |       0 |             126 |    39 |   274 | Charging power-level or delivered-power aggregate/statistic.            |
| SPV_P1_weekend & holiday          | int64   |        289 |       0 |             136 |    50 |   211 | Charging power-level or delivered-power aggregate/statistic.            |
| SPV_P2_weekend & holiday          | int64   |        289 |       0 |             179 |    64 |   399 | Charging power-level or delivered-power aggregate/statistic.            |
| SPV_P3_weekend & holiday          | int64   |        289 |       0 |              24 |     6 |    29 | Charging power-level or delivered-power aggregate/statistic.            |

## usage_pattern

| column                                  | dtype   |   non_null |   nulls |   unique_values |       min |       max | meaning                                                                 |
|:----------------------------------------|:--------|-----------:|--------:|----------------:|----------:|----------:|:------------------------------------------------------------------------|
| time_slot                               | int64   |         97 |       0 |              97 | 0         | 96        | Temporal index or time-of-day field from the aggregated public dataset. |
| Private car_workday_driving             | float64 |         97 |       0 |              96 | 0.0686551 |  0.413237 | Dataset-provided aggregate column; inspect values before modelling.     |
| Private car_workday_charging            | float64 |         97 |       0 |              96 | 0.0385549 |  0.16578  | Dataset-provided aggregate column; inspect values before modelling.     |
| Private car_workday_parked              | float64 |         97 |       0 |              96 | 0.537588  |  0.867305 | Dataset-provided aggregate column; inspect values before modelling.     |
| Private car_weekend & holiday_driving   | float64 |         97 |       0 |              96 | 0.0838308 |  0.354513 | Dataset-provided aggregate column; inspect values before modelling.     |
| Private car_weekend & holiday_charging  | float64 |         97 |       0 |              96 | 0.0391442 |  0.185591 | Dataset-provided aggregate column; inspect values before modelling.     |
| Private car_weekend & holiday_parked    | float64 |         97 |       0 |              96 | 0.54829   |  0.844886 | Dataset-provided aggregate column; inspect values before modelling.     |
| Taxi_workday_driving                    | float64 |         97 |       0 |              96 | 0.0474583 |  0.546141 | Dataset-provided aggregate column; inspect values before modelling.     |
| Taxi_workday_charging                   | float64 |         97 |       0 |              95 | 0.0498188 |  0.337396 | Dataset-provided aggregate column; inspect values before modelling.     |
| Taxi_workday_parked                     | float64 |         97 |       0 |              96 | 0.35381   |  0.785299 | Dataset-provided aggregate column; inspect values before modelling.     |
| Taxi_weekend & holiday_driving          | float64 |         97 |       0 |              96 | 0.0564614 |  0.53593  | Dataset-provided aggregate column; inspect values before modelling.     |
| Taxi_weekend & holiday_charging         | float64 |         97 |       0 |              95 | 0.0587258 |  0.364055 | Dataset-provided aggregate column; inspect values before modelling.     |
| Taxi_weekend & holiday_parked           | float64 |         97 |       0 |              95 | 0.353865  |  0.755737 | Dataset-provided aggregate column; inspect values before modelling.     |
| Official car_workday_driving            | float64 |         97 |       0 |              96 | 0.0797278 |  0.407173 | Dataset-provided aggregate column; inspect values before modelling.     |
| Official car_workday_charging           | float64 |         97 |       0 |              96 | 0.0469434 |  0.165163 | Dataset-provided aggregate column; inspect values before modelling.     |
| Official car_workday_parked             | float64 |         97 |       0 |              96 | 0.49221   |  0.839401 | Dataset-provided aggregate column; inspect values before modelling.     |
| Official car_weekend & holiday_driving  | float64 |         97 |       0 |              96 | 0.106141  |  0.432341 | Dataset-provided aggregate column; inspect values before modelling.     |
| Official car_weekend & holiday_charging | float64 |         97 |       0 |              95 | 0.0567204 |  0.193135 | Dataset-provided aggregate column; inspect values before modelling.     |
| Official car_weekend & holiday_parked   | float64 |         97 |       0 |              95 | 0.463937  |  0.796423 | Dataset-provided aggregate column; inspect values before modelling.     |
| Rental car_workday_driving              | float64 |         97 |       0 |              95 | 0.171287  |  0.48832  | Dataset-provided aggregate column; inspect values before modelling.     |
| Rental car_workday_charging             | float64 |         97 |       0 |              96 | 0.0334436 |  0.150049 | Dataset-provided aggregate column; inspect values before modelling.     |
| Rental car_workday_parked               | float64 |         97 |       0 |              96 | 0.447109  |  0.753514 | Dataset-provided aggregate column; inspect values before modelling.     |
| Rental car_weekend & holiday_driving    | float64 |         97 |       0 |              95 | 0.226071  |  0.585707 | Dataset-provided aggregate column; inspect values before modelling.     |
| Rental car_weekend & holiday_charging   | float64 |         97 |       0 |              92 | 0.045182  |  0.188009 | Dataset-provided aggregate column; inspect values before modelling.     |
| Rental car_weekend & holiday_parked     | float64 |         97 |       0 |              96 | 0.336028  |  0.682066 | Dataset-provided aggregate column; inspect values before modelling.     |
| Bus_workday_driving                     | float64 |         97 |       0 |              95 | 0.0370507 |  0.679672 | Dataset-provided aggregate column; inspect values before modelling.     |
| Bus_workday_charging                    | float64 |         97 |       0 |              96 | 0.030185  |  0.135486 | Dataset-provided aggregate column; inspect values before modelling.     |
| Bus_workday_parked                      | float64 |         97 |       0 |              96 | 0.230655  |  0.919223 | Dataset-provided aggregate column; inspect values before modelling.     |
| Bus_weekend & holiday_driving           | float64 |         97 |       0 |              96 | 0.0355669 |  0.526003 | Dataset-provided aggregate column; inspect values before modelling.     |
| Bus_weekend & holiday_charging          | float64 |         97 |       0 |              96 | 0.0299564 |  0.139186 | Dataset-provided aggregate column; inspect values before modelling.     |
| Bus_weekend & holiday_parked            | float64 |         97 |       0 |              94 | 0.378401  |  0.917936 | Dataset-provided aggregate column; inspect values before modelling.     |
| SPV_workday_driving                     | float64 |         97 |       0 |              96 | 0.102527  |  0.484683 | Dataset-provided aggregate column; inspect values before modelling.     |
| SPV_workday_charging                    | float64 |         97 |       0 |              96 | 0.0363542 |  0.137995 | Dataset-provided aggregate column; inspect values before modelling.     |
| SPV_workday_parked                      | float64 |         97 |       0 |              96 | 0.409079  |  0.825308 | Dataset-provided aggregate column; inspect values before modelling.     |
| SPV_weekend & holiday_driving           | float64 |         97 |       0 |              94 | 0.127178  |  0.513716 | Dataset-provided aggregate column; inspect values before modelling.     |
| SPV_weekend & holiday_charging          | float64 |         97 |       0 |              95 | 0.0421542 |  0.166764 | Dataset-provided aggregate column; inspect values before modelling.     |
| SPV_weekend & holiday_parked            | float64 |         97 |       0 |              96 | 0.368337  |  0.789294 | Dataset-provided aggregate column; inspect values before modelling.     |

## soc

| column        | dtype   |   non_null |   nulls |   unique_values |   min |   max | meaning                                                             |
|:--------------|:--------|-----------:|--------:|----------------:|------:|------:|:--------------------------------------------------------------------|
| vehicle_SOC_P | str     |         36 |      36 |              36 |       |       | Vehicle category/count/statistic field.                             |
| Lower Whisker | float64 |         36 |      36 |               1 |     6 |     6 | Dataset-provided aggregate column; inspect values before modelling. |
| Q1 (25%)      | float64 |         36 |      36 |              14 |    33 |    61 | Dataset-provided aggregate column; inspect values before modelling. |
| Median (50%)  | float64 |         36 |      36 |              12 |    61 |    85 | Dataset-provided aggregate column; inspect values before modelling. |
| Q3 (75%)      | float64 |         36 |      36 |               5 |    94 |    99 | Dataset-provided aggregate column; inspect values before modelling. |
| Upper Whisker | float64 |         36 |      36 |               1 |   100 |   100 | Dataset-provided aggregate column; inspect values before modelling. |

## ecr_temp

| column      | dtype   |   non_null |   nulls |   unique_values |     min |     max | meaning                                                                 |
|:------------|:--------|-----------:|--------:|----------------:|--------:|--------:|:------------------------------------------------------------------------|
| time_slot   | int64   |         84 |       0 |              84 |  0      | 83      | Temporal index or time-of-day field from the aggregated public dataset. |
| Temperature | float64 |         84 |       0 |              77 | -4.6    | 29.2    | Energy-consumption-rate contextual variable.                            |
| ECR         | float64 |         84 |       0 |              82 | 14.7394 | 24.2308 | Energy-consumption-rate contextual variable.                            |

## ecr_month

| column    | dtype   |   non_null |   nulls |   unique_values |     min |     max | meaning                                                                 |
|:----------|:--------|-----------:|--------:|----------------:|--------:|--------:|:------------------------------------------------------------------------|
| time_slot | int64   |         12 |       0 |              12 |  0      | 11      | Temporal index or time-of-day field from the aggregated public dataset. |
| Beijing   | float64 |         12 |       0 |              12 | 15.576  | 24.2308 | Dataset-provided aggregate column; inspect values before modelling.     |
| Shanghai  | float64 |         12 |       0 |              12 | 16.1765 | 20.3618 | Dataset-provided aggregate column; inspect values before modelling.     |
| Guangzhou | float64 |         12 |       0 |              12 | 14.7394 | 17.7358 | Dataset-provided aggregate column; inspect values before modelling.     |
| Shenzhen  | float64 |         12 |       0 |              12 | 16.5291 | 19.1354 | Dataset-provided aggregate column; inspect values before modelling.     |
| Nanjing   | float64 |         12 |       0 |              12 | 16.1538 | 20.2934 | Dataset-provided aggregate column; inspect values before modelling.     |
| Chengdu   | float64 |         12 |       0 |              12 | 15.3204 | 17.8455 | Dataset-provided aggregate column; inspect values before modelling.     |
| Chongqing | float64 |         12 |       0 |              12 | 15.8272 | 18.8559 | Dataset-provided aggregate column; inspect values before modelling.     |

## clusters

| column     | dtype   |   non_null |   nulls |   unique_values |     min |      max | meaning                                                             |
|:-----------|:--------|-----------:|--------:|----------------:|--------:|---------:|:--------------------------------------------------------------------|
| cluster_id | int64   |        144 |       0 |               3 | 0       |  2       | Dataset-provided aggregate column; inspect values before modelling. |
| t          | int64   |        144 |       0 |              24 | 0       | 23       | Dataset-provided aggregate column; inspect values before modelling. |
| q25        | float64 |        144 |       0 |              90 | 0       |  2.53149 | Dataset-provided aggregate column; inspect values before modelling. |
| q50        | float64 |        144 |       0 |             140 | 0       |  9.87707 | Dataset-provided aggregate column; inspect values before modelling. |
| q75        | float64 |        144 |       0 |             144 | 0.80977 | 44.3656  | Dataset-provided aggregate column; inspect values before modelling. |
| Type       | str     |        144 |       0 |               2 |         |          | Dataset-provided aggregate column; inspect values before modelling. |

## driving_dist

| column         | dtype   |   non_null |   nulls |   unique_values |   min |   max | meaning                                                             |
|:---------------|:--------|-----------:|--------:|----------------:|------:|------:|:--------------------------------------------------------------------|
| CDF Percentile | float64 |        100 |       0 |             100 |   1   | 100   | Distribution percentile/CDF support field.                          |
| Private car    | float64 |        100 |       0 |              98 |   6   | 499.4 | Dataset-provided aggregate column; inspect values before modelling. |
| Official car   | float64 |        100 |       0 |             100 |   6   | 499   | Dataset-provided aggregate column; inspect values before modelling. |
| SPV            | float64 |        100 |       0 |             100 |   6.1 | 499   | Dataset-provided aggregate column; inspect values before modelling. |
| Rental car     | float64 |        100 |       0 |             100 |   6   | 499.8 | Dataset-provided aggregate column; inspect values before modelling. |
| Bus            | float64 |        100 |       0 |             100 |  10   | 494   | Dataset-provided aggregate column; inspect values before modelling. |
| Taxi           | float64 |        100 |       0 |             100 |   7   | 499   | Dataset-provided aggregate column; inspect values before modelling. |

## battery_energy

| column        | dtype   |   non_null |   nulls |   unique_values |     min |      max | meaning                                                             |
|:--------------|:--------|-----------:|--------:|----------------:|--------:|---------:|:--------------------------------------------------------------------|
| type_2        | str     |          6 |       0 |               6 |         |          | Dataset-provided aggregate column; inspect values before modelling. |
| Lower Whisker | float64 |          6 |       0 |               4 | 20.2    |  30.8221 | Dataset-provided aggregate column; inspect values before modelling. |
| Q1 (25%)      | float64 |          6 |       0 |               6 | 35      | 104.007  | Dataset-provided aggregate column; inspect values before modelling. |
| Median (50%)  | float64 |          6 |       0 |               6 | 43.6    | 165.88   | Dataset-provided aggregate column; inspect values before modelling. |
| Q3 (75%)      | float64 |          6 |       0 |               5 | 52.7    | 285.6    | Dataset-provided aggregate column; inspect values before modelling. |
| Upper Whisker | float64 |          6 |       0 |               6 | 75.5631 | 374.65   | Dataset-provided aggregate column; inspect values before modelling. |

## energy_ratio

| column        | dtype   |   non_null |   nulls |   unique_values |   min |   max | meaning                                                             |
|:--------------|:--------|-----------:|--------:|----------------:|------:|------:|:--------------------------------------------------------------------|
| type_2        | str     |          6 |       0 |               6 |       |       | Dataset-provided aggregate column; inspect values before modelling. |
| Lower Whisker | int64   |          6 |       0 |               1 | 0     |  0    | Dataset-provided aggregate column; inspect values before modelling. |
| Q1 (25%)      | float64 |          6 |       0 |               6 | 0.07  |  0.49 | Dataset-provided aggregate column; inspect values before modelling. |
| Median (50%)  | float64 |          6 |       0 |               5 | 0.14  |  0.8  | Dataset-provided aggregate column; inspect values before modelling. |
| Q3 (75%)      | float64 |          6 |       0 |               6 | 0.24  |  1.33 | Dataset-provided aggregate column; inspect values before modelling. |
| Upper Whisker | float64 |          6 |       0 |               6 | 0.495 |  2.59 | Dataset-provided aggregate column; inspect values before modelling. |

## charging_freq

| column        | dtype   |   non_null |   nulls |   unique_values |      min |      max | meaning                                                             |
|:--------------|:--------|-----------:|--------:|----------------:|---------:|---------:|:--------------------------------------------------------------------|
| type_2        | str     |          6 |       0 |               6 |          |          | Dataset-provided aggregate column; inspect values before modelling. |
| Lower Whisker | float64 |          6 |       0 |               1 | 0.333333 | 0.333333 | Dataset-provided aggregate column; inspect values before modelling. |
| Q1 (25%)      | float64 |          6 |       0 |               6 | 0.366667 | 1        | Dataset-provided aggregate column; inspect values before modelling. |
| Median (50%)  | float64 |          6 |       0 |               6 | 0.466667 | 1.7      | Dataset-provided aggregate column; inspect values before modelling. |
| Q3 (75%)      | float64 |          6 |       0 |               6 | 0.633333 | 2.96667  | Dataset-provided aggregate column; inspect values before modelling. |
| Upper Whisker | float64 |          6 |       0 |               6 | 1.03333  | 5.91667  | Dataset-provided aggregate column; inspect values before modelling. |

## charger_hist_car

| column    | dtype   |   non_null |   nulls |   unique_values |         min |       max | meaning                                                                 |
|:----------|:--------|-----------:|--------:|----------------:|------------:|----------:|:------------------------------------------------------------------------|
| time_slot | int64   |         60 |       0 |              60 | 0           | 59        | Temporal index or time-of-day field from the aggregated public dataset. |
| Interval  | str     |         60 |       0 |              60 |             |           | Dataset-provided aggregate column; inspect values before modelling.     |
| Height    | float64 |         60 |       0 |              60 | 0.000713687 |  0.319765 | Dataset-provided aggregate column; inspect values before modelling.     |

## charger_hist_bus

| column    | dtype   |   non_null |   nulls |   unique_values |         min |         max | meaning                                                                 |
|:----------|:--------|-----------:|--------:|----------------:|------------:|------------:|:------------------------------------------------------------------------|
| time_slot | int64   |        300 |       0 |             300 | 0           | 299         | Temporal index or time-of-day field from the aggregated public dataset. |
| Interval  | str     |        300 |       0 |             300 |             |             | Dataset-provided aggregate column; inspect values before modelling.     |
| Height    | float64 |        300 |       0 |             289 | 6.96506e-06 |   0.0468836 | Dataset-provided aggregate column; inspect values before modelling.     |

## charger_hist_spv

| column    | dtype   |   non_null |   nulls |   unique_values |         min |         max | meaning                                                                 |
|:----------|:--------|-----------:|--------:|----------------:|------------:|------------:|:------------------------------------------------------------------------|
| time_slot | int64   |        125 |       0 |             125 | 0           | 124         | Temporal index or time-of-day field from the aggregated public dataset. |
| Interval  | str     |        125 |       0 |             125 |             |             | Dataset-provided aggregate column; inspect values before modelling.     |
| Height    | float64 |        125 |       0 |             115 | 7.40977e-06 |   0.0419096 | Dataset-provided aggregate column; inspect values before modelling.     |

