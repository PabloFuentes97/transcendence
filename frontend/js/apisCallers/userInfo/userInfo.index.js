import AcceptFriendRequest from "./acceptFriendRequest.js";
import ChangeAlias from "./changeAlias.js";
import DeclineFriendRequest from "./declineFriendRequest.js";
import ExistAlias from "./existAlias.js";
import AliasAvailable from "./aliasAvailable.js";
import ExistUser from "./existUser.js";
import GetAllUsersInfo from "./getAllUsersInfo.js";
import GetFriendRequest from "./getFriendRequests.js"
import GetFriends from "./getFriends.js";
import GetMyUserInfo from "./getMyUserInfo.js";
import GetUserInfo from "./getUserInfo.js"
import RemoveFriend from "./removeFriend.js"
import SendFriendRequest from "./sendFriendRequest.js"
import UploadProfilePhoto from "./uploadProfilePhoto.js";
import * as MyProfile from "./myProfileGetters.js"

const userInfo = {
	acceptFriendRequest: AcceptFriendRequest,
	changeAlias: ChangeAlias,
	declineFriendRequest: DeclineFriendRequest,
	existAlias: ExistAlias,
	aliasAvailable: AliasAvailable,
	existUser: ExistUser,
	getAllUsersInfo: GetAllUsersInfo,
	getFriendRequest: GetFriendRequest,
	getFriends: GetFriends,
	getMyUserInfo: GetMyUserInfo,
	getUserInfo: GetUserInfo,
	removeFriend: RemoveFriend,
	sendFriendRequest: SendFriendRequest,
	uploadProfilePhoto: UploadProfilePhoto,
	myProfile: MyProfile
}

export {userInfo};