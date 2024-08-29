import userInfoPost from "./userInfoPost.js";

export default async(friendUsername) => {

    const data = await userInfoPost("decline_friend_request", friendUsername);
    return data;
}