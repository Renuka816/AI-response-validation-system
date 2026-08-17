import { useState } from "react";

import Evaluator from "./pages/Evaluator";
import BatchEvaluator from "./pages/BatchEvaluator";
import Dashboard from "./pages/Dashboard";

import "./styles/App.css";

export default function App() {

  const [page, setPage] = useState("single");

  return (
    <>
      {page === "single" && (
        <Evaluator
          goToBatch={() => setPage("batch")}
          goToDashboard={() => setPage("dashboard")}
        />
      )}

      {page === "batch" && (
        <BatchEvaluator
          goBack={() => setPage("single")}
          goToDashboard={() => setPage("dashboard")}
        />
      )}

      {page === "dashboard" && (
        <Dashboard
          goToSingle={() => setPage("single")}
          goToBatch={() => setPage("batch")}
        />
      )}
    </>
  );
}