export async function get_text_lang(id) {
    let url = new URL(window.location.href);
	let params = new URLSearchParams(url.search);
	let lang = params.get('lang');
    if (!lang || !['en', 'fr', 'es'].includes(lang)) {
        lang = 'en';
    }
    let text = null;
    try {
        let response = await fetch(`/assets/langues/${lang}.json`);
        if (!response.ok) {
            throw new Error('La langue n\'est pas trouvée, chargement de la langue par défaut');
        }
        let data = await response.json();
        text = data[id];
    } catch (error) {
        console.error(error);
    }
    return text;
}
