import "../styles/InputCard.css";

export default function InputCard({
  title,
  icon,
  placeholder,
  value,
  onChange,
  maxLength
}) {

  return (

    <div className="input-card">

      <div className="input-header">

        <div className="icon">

          {icon}

        </div>

        <label>{title}</label>

      </div>

      <textarea

        placeholder={placeholder}

        value={value}

        maxLength={maxLength}

        onChange={(e)=>onChange(e.target.value)}

      />

      <div className="counter">

        {value.length}/{maxLength}

      </div>

    </div>

  );

}