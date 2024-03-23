export function draw_game_menu() {
	// console.log("draw_game_menu");
	document.getElementById("game_menu").style.display = 'flex';
}

export function draw_ingame_menu() {
	// console.log("draw_ingame_menu");
	document.getElementById("pongCanvas").style.display = '';
	document.getElementById("in_game").style.display = 'flex';
}

export function draw_endgame_menu() {
	// console.log("draw_endgame_menu");
	document.getElementById("end_game").style.display = 'flex';
}

export function draw_tournament_menu() {
	// console.log("draw_tournament_menu");
	document.getElementById("pongCanvas").style.display = '';
	document.getElementById("end_game_tournament").style.display = 'flex';
}

export function hide_game_menu()
{
	// console.log("hide_game_menu");
	document.getElementById("game_menu").style.display = 'none';
	document.getElementById("in_game").style.display = 'none';
	document.getElementById("end_game").style.display = 'none';
	document.getElementById("end_game_tournament").style.display = 'none';
}

export function show_hide_canvas(value) {
	// console.log("show_hide_canvas");
	if (value === "hide")
		document.getElementById("pongCanvas").style.display = 'none';
	else if (value === "show")
		document.getElementById("pongCanvas").style.display = 'block';
}