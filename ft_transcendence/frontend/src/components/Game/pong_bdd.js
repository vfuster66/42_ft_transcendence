import { getCookie } from "../../main.js";

export function update_score(player, opponent, score_to_add, won_or_lost, playerPoints, opponentPoints){
	// console.log("update score : player :", player, ", score_to_add : ", score_to_add, ", won_or_lost : ", won_or_lost);
    $.ajax({
        url: '/api/update-score/',  // URL of your Django view
        type: 'POST',
        data: {'player': player,
				'score': score_to_add,
				'won': won_or_lost,
                'opponent': opponent,
                'playerPoints': playerPoints,
                'opponentPoints': opponentPoints},
        beforeSend: function(xhr) {
            xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
        },
        success: function(data) {
            if (data.error)
                console.error("Error: ", data.error);
        },
        error: function(xhr, status, error) {
        }
    });
}
