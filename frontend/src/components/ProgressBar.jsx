export default function ProgressBar({ value }) {

  return (

    <div className="progress">

      <div
        className="progress-fill"
        style={{ width: `${value}%` }}
      />

    </div>

  );

}