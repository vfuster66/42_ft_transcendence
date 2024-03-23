import { get_highscores } from "../../components/highscores.js";

export function changeLanguage(lang) {
	if (!lang || !['en', 'fr', 'es'].includes(lang)) {
        lang = 'en';
    }
	// Chargez le fichier de langue approprié en fonction de 'lang'
	fetch(`/assets/langues/${lang}.json`)
		.then(response => {
			if (!response.ok) {
				throw new Error('La langue n\'est pas trouvée, chargement de la langue par défaut');
			}
			return response.json();
		})
		.then(data2 => {
		document.getElementById('login_with_42_Button').textContent = data2.login_with_42_Button;
		document.getElementById('normal_login_Button').textContent = data2.normal_login_Button;
		document.getElementById('menu_Button').textContent = data2.menu_Button;
		document.getElementById('gamePlayed').textContent = data2.divprofilegames;
		document.getElementById('gameWons').textContent = data2.divprofilewons;
		document.getElementById('gameScore').textContent = data2.divprofilescore;
		document.getElementById('vsbtn').textContent = data2.vsbtn;
		document.getElementById('aibtn').textContent = data2.aibtn;
		document.getElementById('modbtn').textContent = data2.modbtn;
		document.getElementById('tourbtn').textContent = data2.tourbtn;
		document.getElementById("startbtn").textContent = data2.startbtn;
		document.getElementById("pausebtn").textContent = data2.pausebtn;
		document.getElementById("quitbtn").textContent = data2.quitbtn;
		document.getElementById("quit2btn").textContent = data2.quit2btn;
		document.getElementById("quit3btn").textContent = data2.quit3btn;
		document.getElementById("ngbtn").textContent = data2.ngbtn;
		document.getElementById("nextbtn").textContent = data2.nextbtn;
		document.getElementById("profil-Btn").setAttribute('title', data2.profilBtn);
		document.getElementById("game-Btn").setAttribute('title', data2.gameBtn);
		document.getElementById("leaderboard-Btn").setAttribute('title', data2.leaderboardBtn);
		document.getElementById("settings-Btn").setAttribute('title', data2.settingsBtn);
		document.getElementById("credits-Btn").setAttribute('title', data2.creditsBtn);
		document.getElementById("logout-Button").setAttribute('title', data2.logoutBtn);
		document.getElementById("settings-username").textContent = data2.settingname;
		document.getElementById("settings-mail").textContent = data2.settingmail;
		document.getElementById("settings-password").textContent = data2.settingpassword;
		document.getElementById("settings-onemoretime").textContent = data2.settingonemoretime;
		document.getElementById("password-strength").textContent = data2.settingminimum;
		document.getElementById("change-info").setAttribute('value', data2.settingchange);
		document.getElementById("setting-change-password").setAttribute('value', data2.settingchangepassword);
		document.getElementById("change-user-info").textContent = data2.changeuserinfo;
		document.getElementById("config2fatitle").textContent = data2.config2fatitle;
		document.getElementById("changephototext").textContent = data2.changephototext;
		document.getElementById("2fa-switch-text").textContent = data2.twofaswitchtext;
		document.getElementById("friend-list-h4").textContent = data2.friendlisttitle;
		document.getElementById("add-friend-input").setAttribute('placeholder', data2.addfriendinput);
		document.getElementById("add-friend-btn").setAttribute('value', data2.addfriendbtn);
		document.getElementById("input-file").setAttribute('value', data2.inputfile);
		document.getElementById("last-game-title").textContent = data2.lastgametitle;
		if (document.getElementById("HS_Score")){
			document.getElementById("HS_Score").textContent = data2.score;
			document.getElementById("HS_Games").textContent = data2.total_games;
			document.getElementById("HS_Ratio").textContent = data2.wonLoss;
			document.getElementById("HS_Player").textContent = data2.player;
		}
		// Multiplayer window
		document.getElementById("multi-text").textContent = data2.multi_title;
		document.getElementById("add-player-btn").value = data2.multi_add;
		document.getElementById("multi-btn").value = data2.multi_close;
		let elements = document.querySelectorAll('[id^="submit-p"]');
		elements.forEach(element => {
			element.value = data2.multi_login;
		});
		elements = document.getElementsByClassName('mp-pass');
		for (let i = 0; i < elements.length; i++) {
				elements[i].textContent = data2.settingpassword;
		}


		elements = document.getElementsByClassName('btn-link-intra');
		for (let i = 0; i < elements.length; i++) {
				elements[i].textContent = data2.btnlinkintra;
		}

		let url = new URL(window.location.href);
		url.searchParams.set('lang', lang);
		window.history.pushState({lang: lang}, '', url.href);
	})
	.catch(error => {
		console.error('Erreur lors du chargement du fichier de langue:', error);
		if (lang !== 'en') { // Si la langue par défaut n'est pas 'en', essayez de charger 'en'
			changeLanguage('en');
		}
	});
}
