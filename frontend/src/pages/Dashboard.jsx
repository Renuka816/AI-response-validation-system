import { useEffect, useMemo, useState } from "react";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line
} from "recharts";

import API from "../services/api";
import Header from "../components/Header";


// =========================================================
// DASHBOARD
// =========================================================

export default function Dashboard({
  goToSingle,
  goToBatch
}) {

  const [summary, setSummary] = useState(null);
  const [evaluations, setEvaluations] = useState([]);
  const [trends, setTrends] = useState([]);

  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");


  // =======================================================
  // FILTER STATE
  // =======================================================

  const [evaluationMode, setEvaluationMode] = useState("");
  const [model, setModel] = useState("");
  const [dataset, setDataset] = useState("");

  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const [appliedFilters, setAppliedFilters] = useState({
    evaluation_mode: "",
    model: "",
    dataset: "",
    date_from: "",
    date_to: ""
  });


  // =======================================================
  // LOAD DASHBOARD
  // =======================================================

  const loadDashboard = async (filters = appliedFilters) => {

    setLoading(true);
    setErrorMessage("");

    try {

      const params = {};

      if (filters.evaluation_mode) {
        params.evaluation_mode =
          filters.evaluation_mode;
      }

      if (filters.model) {
        params.model = filters.model;
      }

      if (filters.dataset) {
        params.dataset = filters.dataset;
      }

      if (filters.date_from) {
        params.date_from = filters.date_from;
      }

      if (filters.date_to) {
        params.date_to = filters.date_to;
      }


      const [
        summaryRes,
        evaluationsRes,
        trendsRes
      ] = await Promise.all([

        API.get(
          "/dashboard/summary",
          { params }
        ),

        API.get(
          "/dashboard/evaluations",
          { params }
        ),

        API.get(
          "/dashboard/trends",
          { params }
        )

      ]);


      setSummary(summaryRes.data);


      setEvaluations(
        Array.isArray(evaluationsRes.data)
          ? evaluationsRes.data
          : []
      );


      setTrends(
        Array.isArray(trendsRes.data)
          ? trendsRes.data
          : []
      );

    }

    catch (error) {

      console.error(
        "Dashboard loading failed:",
        error
      );

      setErrorMessage(
        "Failed to load dashboard data."
      );

    }

    finally {

      setLoading(false);

    }

  };


  // =======================================================
  // INITIAL LOAD
  // =======================================================

  useEffect(() => {

    loadDashboard();

  }, []);


  // =======================================================
  // AVAILABLE MODELS
  // =======================================================

  const availableModels = useMemo(() => {

    return [
      ...new Set(
        evaluations
          .map(item => item.model)
          .filter(Boolean)
      )
    ];

  }, [evaluations]);


  // =======================================================
  // AVAILABLE DATASETS
  // =======================================================

  const availableDatasets = useMemo(() => {

    return [
      ...new Set(
        evaluations
          .map(item => item.dataset)
          .filter(Boolean)
      )
    ];

  }, [evaluations]);


  // =======================================================
  // APPLY FILTERS
  // =======================================================

  const applyFilters = () => {

    if (
      dateFrom &&
      dateTo &&
      dateFrom > dateTo
    ) {

      setErrorMessage(
        "From Date cannot be later than To Date."
      );

      return;

    }


    const filters = {

      evaluation_mode:
        evaluationMode,

      model:
        model,

      dataset:
        dataset,

      date_from:
        dateFrom,

      date_to:
        dateTo

    };


    setAppliedFilters(filters);

    loadDashboard(filters);

  };


  // =======================================================
  // RESET FILTERS
  // =======================================================

    // ---------------------------------------------------------
// Export Evaluation Report
// ---------------------------------------------------------

const exportReport = async () => {

  try {

    const params = {};

    if (evaluationMode)
      params.evaluation_mode = evaluationMode;

    if (model)
      params.model = model;

    if (dataset)
      params.dataset = dataset;

    if (dateFrom)
      params.date_from = dateFrom;

    if (dateTo)
      params.date_to = dateTo;


    const response = await API.get(
      "/dashboard/report/pdf",
      {
        params,
        responseType: "blob"
      }
    );


    const blob = new Blob(
      [response.data],
      {
        type: "application/pdf"
      }
    );


    const url =
      window.URL.createObjectURL(blob);


    const link =
      document.createElement("a");

    link.href = url;

    link.download =
      "AI_Response_Quality_Evaluation_Report.pdf";

    document.body.appendChild(link);

    link.click();

    link.remove();

    window.URL.revokeObjectURL(url);

  }

  catch (error) {

    console.error(
      "Report export failed:",
      error
    );

    alert(
      "Failed to generate evaluation report."
    );

  }

};


  const resetFilters = () => {

    const emptyFilters = {

      evaluation_mode: "",
      model: "",
      dataset: "",
      date_from: "",
      date_to: ""

    };


    setEvaluationMode("");
    setModel("");
    setDataset("");

    setDateFrom("");
    setDateTo("");

    setAppliedFilters(emptyFilters);

    loadDashboard(emptyFilters);

  };


  // =======================================================
  // QUALITY DIMENSIONS
  // =======================================================

  const qualityData = [

    {
      name: "Accuracy",
      score:
        Number(
          summary?.average_accuracy ?? 0
        )
    },

    {
      name: "Relevance",
      score:
        Number(
          summary?.average_relevance ?? 0
        )
    },

    {
      name: "Completeness",
      score:
        Number(
          summary?.average_completeness ?? 0
        )
    },

    {
      name: "Hallucination",
      score:
        Number(
          summary?.average_hallucination ?? 0
        )
    }

  ];


  // =======================================================
  // RESULT DISTRIBUTION
  // =======================================================

  const resultData = [

    {
      name: "Pass",
      value:
        Number(
          summary?.pass_count ?? 0
        )
    },

    {
      name: "Needs Improvement",
      value:
        Number(
          summary?.needs_improvement_count ?? 0
        )
    },

    {
      name: "Fail",
      value:
        Number(
          summary?.fail_count ?? 0
        )
    }

  ];


  const PIE_COLORS = [
    "#22c55e",
    "#f59e0b",
    "#ef4444"
  ];


  // =======================================================
  // TREND DATA
  // =======================================================

  const trendData = useMemo(() => {

    return trends.map(
      (item, index) => {

        let formattedDate =
          `Evaluation ${index + 1}`;

        let fullTimestamp =
          item.timestamp || "Unknown";


        if (item.timestamp) {

          const parsedDate =
            new Date(item.timestamp);


          if (
            !Number.isNaN(
              parsedDate.getTime()
            )
          ) {

            formattedDate =
              parsedDate.toLocaleDateString(
                "en-GB",
                {
                  day: "2-digit",
                  month: "short"
                }
              );

          }
        }


        return {

          index:
            index + 1,

          date:
            formattedDate,

          timestamp:
            fullTimestamp,

          accuracy:
            Number(
              item.accuracy_score ?? 0
            ),

          relevance:
            Number(
              item.relevance_score ?? 0
            ),

          completeness:
            Number(
              item.completeness_score ?? 0
            ),

          overall:
            Number(
              item.final_score ?? 0
            )

        };

      }
    );

  }, [trends]);


  // =======================================================
  // LOADING SCREEN
  // =======================================================

  if (loading) {

    return (

      <div className="app">

        <Header />

        <div className="glass-container">

          <h2
            style={{
              color: "white",
              textAlign: "center",
              padding: "60px"
            }}
          >
            Loading Dashboard...
          </h2>

        </div>

      </div>

    );

  }


  // =======================================================
  // DASHBOARD UI
  // =======================================================

  return (

    <div className="app">

      <Header />


      <div className="glass-container">


        {/* ================================================= */}
        {/* NAVIGATION */}
        {/* ================================================= */}

        <div
          style={{
            display: "flex",
            gap: "12px",
            marginBottom: "30px",
            flexWrap: "wrap"
          }}
        >

          <button
            className="gradient-button"
            onClick={goToSingle}
          >
            ← Single Evaluation
          </button>


          <button
            className="gradient-button"
            onClick={goToBatch}
          >
            📂 Batch Evaluation
          </button>

          <button
            onClick={exportReport}
            style={{
              padding: "12px 24px",
              borderRadius: "12px",
              border: "none",
              background: "linear-gradient(135deg, #10b981 0%, #059669 100%)",
              color: "white",
              fontWeight: "600",
              fontSize: "15px",
              cursor: "pointer",
              marginLeft: "auto",
              boxShadow: "0 4px 14px rgba(16, 185, 129, 0.4)",
              transition: "0.3s"
            }}
          >
            📥 Export PDF Report
          </button>
        </div>


        {/* ================================================= */}
        {/* TITLE */}
        {/* ================================================= */}

        <h1
          style={{
            color: "white",
            textAlign: "center",
            fontSize: "34px",
            marginBottom: "8px"
          }}
        >
          Evaluation Scoring Dashboard
        </h1>


        <p
          style={{
            color: "#94a3b8",
            textAlign: "center",
            marginBottom: "30px"
          }}
        >
          Monitor AI response quality across all evaluations
        </p>


        {/* ================================================= */}
        {/* ERROR */}
        {/* ================================================= */}

        {errorMessage && (

          <div
            style={{
              background: "rgba(239,68,68,0.12)",
              border: "1px solid #ef4444",
              color: "#fca5a5",
              padding: "12px 16px",
              borderRadius: "10px",
              marginBottom: "20px",
              textAlign: "center"
            }}
          >
            {errorMessage}
          </div>

        )}


        {/* ================================================= */}
        {/* FILTERS */}
        {/* ================================================= */}

        <div
          className="glass-card"
          style={{
            padding: "22px",
            marginBottom: "32px"
          }}
        >

          <h2
            style={{
              color: "white",
              marginBottom: "20px"
            }}
          >
            Dashboard Filters
          </h2>


          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit,minmax(180px,1fr))",
              gap: "16px"
            }}
          >


            {/* FROM DATE */}

            <div>

              <label style={labelStyle}>
                From Date
              </label>

              <input
                type="date"
                value={dateFrom}
                max={dateTo || undefined}
                onChange={
                  e =>
                    setDateFrom(
                      e.target.value
                    )
                }
                style={inputStyle}
              />

            </div>


            {/* TO DATE */}

            <div>

              <label style={labelStyle}>
                To Date
              </label>

              <input
                type="date"
                value={dateTo}
                min={dateFrom || undefined}
                onChange={
                  e =>
                    setDateTo(
                      e.target.value
                    )
                }
                style={inputStyle}
              />

            </div>


            {/* EVALUATION MODE */}

            <div>

              <label style={labelStyle}>
                Evaluation Mode
              </label>

              <select
                value={evaluationMode}
                onChange={
                  e =>
                    setEvaluationMode(
                      e.target.value
                    )
                }
                style={inputStyle}
              >

                <option value="">
                  All Modes
                </option>

                <option value="single">
                  Single
                </option>

                <option value="batch">
                  Batch
                </option>

              </select>

            </div>


            {/* MODEL */}

            <div>

              <label style={labelStyle}>
                Model
              </label>

              <select
                value={model}
                onChange={
                  e =>
                    setModel(
                      e.target.value
                    )
                }
                style={inputStyle}
              >

                <option value="">
                  All Models
                </option>

                {availableModels.map(
                  item => (

                    <option
                      key={item}
                      value={item}
                    >
                      {item}
                    </option>

                  )
                )}

              </select>

            </div>


            {/* DATASET */}

            <div>

              <label style={labelStyle}>
                Dataset
              </label>

              <select
                value={dataset}
                onChange={
                  e =>
                    setDataset(
                      e.target.value
                    )
                }
                style={inputStyle}
              >

                <option value="">
                  All Datasets
                </option>

                {availableDatasets.map(
                  item => (

                    <option
                      key={item}
                      value={item}
                    >
                      {item}
                    </option>

                  )
                )}

              </select>

            </div>


            {/* APPLY */}

            <div
              style={{
                display: "flex",
                alignItems: "end"
              }}
            >

              <button
                onClick={applyFilters}
                style={{
                  width: "100%",
                  padding: "11px",
                  borderRadius: "8px",
                  border: "none",
                  background:
                    "linear-gradient(135deg,#4f8cff,#7c3aed)",
                  color: "white",
                  cursor: "pointer",
                  fontWeight: "700"
                }}
              >
                Apply Filters
              </button>

            </div>


            {/* RESET */}

            <div
              style={{
                display: "flex",
                alignItems: "end"
              }}
            >

              <button
                onClick={resetFilters}
                style={{
                  width: "100%",
                  padding: "11px",
                  borderRadius: "8px",
                  border:
                    "1px solid #475569",
                  background:
                    "#334155",
                  color: "white",
                  cursor: "pointer",
                  fontWeight: "600"
                }}
              >
                Reset Filters
              </button>

            </div>

          </div>

        </div>


        {/* ================================================= */}
        {/* SUMMARY — ROW 1 */}
        {/* ================================================= */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(2,minmax(0,1fr))",
            gap: "18px",
            marginBottom: "18px"
          }}
        >

          <SummaryCard
            title="Total Evaluations"
            value={
              summary?.total_evaluations ?? 0
            }
          />


          <SummaryCard
            title="Average Score"
            value={
              summary?.average_score ?? 0
            }
          />

        </div>


        {/* ================================================= */}
        {/* SUMMARY — ROW 2 */}
        {/* ================================================= */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(3,minmax(0,1fr))",
            gap: "18px",
            marginBottom: "18px"
          }}
        >

          <SummaryCard
            title="Pass"
            value={
              summary?.pass_count ?? 0
            }
          />


          <SummaryCard
            title="Needs Improvement"
            value={
              summary?.needs_improvement_count ?? 0
            }
          />


          <SummaryCard
            title="Fail"
            value={
              summary?.fail_count ?? 0
            }
          />

        </div>


        {/* ================================================= */}
        {/* SUMMARY — ROW 3: AGENTS */}
        {/* ================================================= */}

        <h2
          style={{
            color: "white",
            fontSize: "20px",
            marginTop: "28px",
            marginBottom: "15px"
          }}
        >
          Agent Quality Scores
        </h2>


        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(4,minmax(0,1fr))",
            gap: "18px",
            marginBottom: "18px"
          }}
        >

          <SummaryCard
            title="Accuracy"
            value={
              summary?.average_accuracy ?? 0
            }
          />


          <SummaryCard
            title="Relevance"
            value={
              summary?.average_relevance ?? 0
            }
          />


          <SummaryCard
            title="Completeness"
            value={
              summary?.average_completeness ?? 0
            }
          />


          <SummaryCard
            title="Hallucination"
            value={
              summary?.average_hallucination ?? 0
            }
          />

        </div>


        {/* ================================================= */}
        {/* SUMMARY — ROW 4 */}
        {/* ================================================= */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(2,minmax(0,1fr))",
            gap: "18px",
            marginBottom: "35px"
          }}
        >

          <SummaryCard
            title="Hallucinations Detected"
            value={
              summary?.hallucination_count ?? 0
            }
          />


          <SummaryCard
            title="Hallucination Frequency"
            value={
              `${summary?.hallucination_frequency ?? 0}%`
            }
          />

        </div>


        {/* ================================================= */}
        {/* CHARTS */}
        {/* ================================================= */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit,minmax(420px,1fr))",
            gap: "20px",
            marginBottom: "35px"
          }}
        >


          {/* ================================================= */}
          {/* QUALITY DIMENSIONS */}
          {/* ================================================= */}

          <div
            className="glass-card"
            style={{
              padding: "20px"
            }}
          >

            <h2 style={chartTitle}>
              Quality Dimensions
            </h2>

            <p style={chartSubtitle}>
              Average score produced by each evaluation agent.
            </p>


            <ResponsiveContainer
              width="100%"
              height={320}
            >

              <BarChart
                data={qualityData}
                margin={{
                  top: 15,
                  right: 15,
                  left: 0,
                  bottom: 20
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#475569"
                />


                <XAxis
                  dataKey="name"
                  stroke="#cbd5e1"
                  interval={0}
                  tick={{
                    fontSize: 12
                  }}
                />


                <YAxis
                  domain={[0, 100]}
                  stroke="#cbd5e1"
                />


                <Tooltip
                  contentStyle={{
                    background:
                      "#1e293b",
                    border:
                      "1px solid #475569",
                    borderRadius:
                      "8px",
                    color: "white"
                  }}
                />


                <Bar
                  dataKey="score"
                  name="Score"
                  fill="#4f8cff"
                  radius={[
                    6,
                    6,
                    0,
                    0
                  ]}
                />

              </BarChart>

            </ResponsiveContainer>

          </div>


          {/* ================================================= */}
          {/* RESULT DISTRIBUTION */}
          {/* ================================================= */}

          <div
            className="glass-card"
            style={{
              padding: "20px"
            }}
          >

            <h2 style={chartTitle}>
              Evaluation Results
            </h2>

            <p style={chartSubtitle}>
              Distribution of Pass, Needs Improvement and Fail results.
            </p>


            <ResponsiveContainer
              width="100%"
              height={320}
            >

              <PieChart>

                <Pie
                  data={resultData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="48%"
                  outerRadius={95}
                  labelLine
                  label
                >

                  {resultData.map(
                    (entry, index) => (

                      <Cell
                        key={
                          `cell-${index}`
                        }
                        fill={
                          PIE_COLORS[index]
                        }
                      />

                    )
                  )}

                </Pie>


                <Tooltip
                  contentStyle={{
                    background:
                      "#1e293b",
                    border:
                      "1px solid #475569",
                    borderRadius:
                      "8px",
                    color: "white"
                  }}
                />


                <Legend />

              </PieChart>

            </ResponsiveContainer>

          </div>

        </div>


        {/* ================================================= */}
        {/* QUALITY TRENDS */}
        {/* ================================================= */}

        <div
          className="glass-card"
          style={{
            padding: "22px",
            marginBottom: "35px"
          }}
        >

          <h2 style={chartTitle}>
            Quality Trends Over Time
          </h2>

          <p style={chartSubtitle}>
            Track response quality across evaluations by date.
          </p>


          {trendData.length === 0 ? (

            <p
              style={{
                color: "#94a3b8",
                textAlign: "center",
                padding: "50px"
              }}
            >
              No trend data available for the selected filters.
            </p>

          ) : (

            <ResponsiveContainer
              width="100%"
              height={380}
            >

              <LineChart
                data={trendData}
                margin={{
                  top: 15,
                  right: 25,
                  left: 5,
                  bottom: 30
                }}
              >

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#475569"
                />


                <XAxis
                  dataKey="date"
                  stroke="#cbd5e1"
                  interval={0}
                  angle={-25}
                  textAnchor="end"
                  height={65}
                  tick={{
                    fontSize: 12
                  }}
                />


                <YAxis
                  domain={[0, 100]}
                  stroke="#cbd5e1"
                />


                <Tooltip
                  content={
                    <CustomTrendTooltip />
                  }
                />


                <Legend />


                <Line
                  type="monotone"
                  dataKey="accuracy"
                  name="Accuracy"
                  stroke="#22c55e"
                  strokeWidth={2.5}
                  dot={{
                    r: 4
                  }}
                  activeDot={{
                    r: 7
                  }}
                />


                <Line
                  type="monotone"
                  dataKey="completeness"
                  name="Completeness"
                  stroke="#a855f7"
                  strokeWidth={2.5}
                  dot={{
                    r: 4
                  }}
                  activeDot={{
                    r: 7
                  }}
                />


                <Line
                  type="monotone"
                  dataKey="overall"
                  name="Overall Score"
                  stroke="#4f8cff"
                  strokeWidth={2.5}
                  dot={{
                    r: 4
                  }}
                  activeDot={{
                    r: 7
                  }}
                />


                <Line
                  type="monotone"
                  dataKey="relevance"
                  name="Relevance"
                  stroke="#f59e0b"
                  strokeWidth={2.5}
                  dot={{
                    r: 4
                  }}
                  activeDot={{
                    r: 7
                  }}
                />

              </LineChart>

            </ResponsiveContainer>

          )}

        </div>


        {/* ================================================= */}
        {/* EVALUATION HISTORY */}
        {/* ================================================= */}

        <h2
          style={{
            color: "white",
            marginBottom: "20px"
          }}
        >
          Evaluation History
        </h2>


        {evaluations.length === 0 ? (

          <p
            style={{
              color: "#94a3b8",
              textAlign: "center",
              padding: "40px"
            }}
          >
            No evaluations found for the selected filters.
          </p>

        ) : (

          evaluations.map(
            (item, index) => (

              <div
                key={
                  item.id || index
                }
                className="glass-card"
                style={{
                  marginBottom: "15px",
                  padding: "20px"
                }}
              >

                <div
                  style={{
                    display: "flex",
                    justifyContent:
                      "space-between",
                    alignItems:
                      "center",
                    gap: "20px"
                  }}
                >


                  <div>

                    <h3
                      style={{
                        color: "white",
                        marginBottom:
                          "8px"
                      }}
                    >
                      {item.question}
                    </h3>


                    <p
                      style={{
                        color:
                          "#94a3b8",
                        margin:
                          "4px 0"
                      }}
                    >
                      Mode:{" "}
                      {
                        item.evaluation_mode ||
                        "single"
                      }
                    </p>


                    {item.model && (

                      <p
                        style={{
                          color:
                            "#64748b",
                          margin:
                            "4px 0",
                          fontSize:
                            "13px"
                        }}
                      >
                        Model: {item.model}
                      </p>

                    )}


                    {item.dataset && (

                      <p
                        style={{
                          color:
                            "#64748b",
                          margin:
                            "4px 0",
                          fontSize:
                            "13px"
                        }}
                      >
                        Dataset: {item.dataset}
                      </p>

                    )}


                    {item.timestamp && (

                      <p
                        style={{
                          color:
                            "#64748b",
                          fontSize:
                            "13px",
                          marginTop:
                            "8px"
                        }}
                      >
                        {formatTimestamp(
                          item.timestamp
                        )}
                      </p>

                    )}

                  </div>


                  <div
                    style={{
                      textAlign:
                        "right",
                      minWidth:
                        "110px"
                    }}
                  >

                    <h2
                      style={{
                        color:
                          "#4f8cff",
                        margin: 0
                      }}
                    >
                      {
                        Number(
                          item.final_score ??
                          0
                        ).toFixed(2)
                      }
                      /100
                    </h2>


                    <p
                      style={{
                        color:
                          item.grade ===
                          "Good"
                            ? "#22c55e"
                            : item.grade ===
                              "Poor"
                            ? "#ef4444"
                            : "#f59e0b",

                        margin:
                          "5px 0",

                        fontWeight:
                          "600"
                      }}
                    >
                      {item.grade}
                    </p>

                  </div>

                </div>

              </div>

            )
          )

        )}

      </div>

    </div>

  );

}


// =========================================================
// SUMMARY CARD
// =========================================================

function SummaryCard({
  title,
  value
}) {

  return (

    <div
      className="summary-card"
      style={{
        minHeight: "105px"
      }}
    >

      <h4>
        {title}
      </h4>

      <h2>
        {value}
      </h2>

    </div>

  );

}


// =========================================================
// TREND TOOLTIP
// =========================================================

function CustomTrendTooltip({
  active,
  payload
}) {

  if (
    !active ||
    !payload ||
    !payload.length
  ) {

    return null;

  }


  const item =
    payload[0].payload;


  return (

    <div
      style={{
        background:
          "#1e293b",

        border:
          "1px solid #475569",

        borderRadius:
          "10px",

        padding:
          "14px 16px",

        color:
          "white",

        boxShadow:
          "0 8px 25px rgba(0,0,0,0.35)"
      }}
    >

      <p
        style={{
          margin:
            "0 0 10px",

          fontWeight:
            "700",

          color:
            "white"
        }}
      >
        {formatTimestamp(
          item.timestamp
        )}
      </p>


      <p
        style={{
          margin:
            "5px 0",

          color:
            "#22c55e"
        }}
      >
        Accuracy:{" "}
        {item.accuracy.toFixed(2)}
      </p>


      <p
        style={{
          margin:
            "5px 0",

          color:
            "#a855f7"
        }}
      >
        Completeness:{" "}
        {item.completeness.toFixed(2)}
      </p>


      <p
        style={{
          margin:
            "5px 0",

          color:
            "#4f8cff"
        }}
      >
        Overall Score:{" "}
        {item.overall.toFixed(2)}
      </p>


      <p
        style={{
          margin:
            "5px 0",

          color:
            "#f59e0b"
        }}
      >
        Relevance:{" "}
        {item.relevance.toFixed(2)}
      </p>

    </div>

  );

}


// =========================================================
// FORMAT TIMESTAMP
// =========================================================

function formatTimestamp(timestamp) {

  if (!timestamp) {
    return "Unknown";
  }


  const date =
    new Date(timestamp);


  if (
    Number.isNaN(
      date.getTime()
    )
  ) {

    return timestamp;

  }


  return date.toLocaleString(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit"
    }
  );

}


// =========================================================
// STYLES
// =========================================================

const chartTitle = {

  color: "white",

  marginBottom: "6px",

  fontSize: "22px"

};


const chartSubtitle = {

  color: "#94a3b8",

  marginTop: "0",

  marginBottom: "10px",

  fontSize: "14px"

};


const labelStyle = {

  color: "#94a3b8",

  display: "block",

  marginBottom: "7px",

  fontSize: "14px",

  fontWeight: "600"

};


const inputStyle = {

  width: "100%",

  boxSizing: "border-box",

  padding: "11px",

  borderRadius: "8px",

  border:
    "1px solid #475569",

  background:
    "#1e293b",

  color: "white",

  outline: "none",

  cursor: "pointer"

};