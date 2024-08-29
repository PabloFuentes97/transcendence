export function createFlashbang() {
    // Create the div element
    let flashbang = document.createElement('div');
    flashbang.id = 'flashbang';
    flashbang.className = 'tc-flashbang';

    // Append the div to the body
    document.body.appendChild(flashbang);

    // Set a timeout to start the fade out after 2 seconds
    setTimeout(() => {
        flashbang.classList.add('fade');
    }, 1000);

    // Remove the element from the DOM after the transition ends (4 seconds total)
    setTimeout(() => {
        document.body.removeChild(flashbang);
    }, 3000);
}