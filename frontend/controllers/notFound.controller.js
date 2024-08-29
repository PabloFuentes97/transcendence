
export default async function() {
	// try catch?
	// return `<p> 404 not found </p>`
	const response = await fetch('/html/404.html');
	if (!response.ok)
		return "404";
	return response.text();
};