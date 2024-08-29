import userInfoPost from "./userInfoPost.js";

export default async(friendUsername) => {

    const data = await userInfoPost("remove_friend", friendUsername);
    return data;
}