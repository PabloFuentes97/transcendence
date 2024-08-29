import Login from "./login.controller.js"
import Home from "./home.controller.js"
import Leaderboard from "./leaderboard.controller.js"
import Profile from "./profile.controller.js"
import Social from "./social.controller.js"
import Play from "./play.controller.js"
import Settings from "./settings.controller.js"
import NotFound from "./notFound.controller.js"
import Game from "./game.controller.js"

const pages = {
	login: Login,
	home: Home,
	leaderboard: Leaderboard,
	profile: Profile,
	play: Play,
	social: Social,
	settings: Settings,
	notFound: NotFound,
	game: Game,
}

export {pages};