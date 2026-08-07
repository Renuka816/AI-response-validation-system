import "../styles/Button.css";

export default function GradientButton({

    onClick,
    loading

}){

    return(

        <button

        className="gradient-btn"

        onClick={onClick}

        disabled={loading}

        >

        {

            loading

            ?

            "Evaluating..."

            :

            "✨ Evaluate Response"

        }

        </button>

    )

}