import { useState } from "react";

import Evaluator from "./pages/Evaluator";
import BatchEvaluator from "./pages/BatchEvaluator";

import "./styles/App.css";

export default function App() {

  const [page, setPage] = useState("single");

  return (
    <>
      {page === "single" ? (
        <Evaluator goToBatch={() => setPage("batch")} />
      ) : (
        <BatchEvaluator goBack={() => setPage("single")} />
      )}
    </>
  );
}