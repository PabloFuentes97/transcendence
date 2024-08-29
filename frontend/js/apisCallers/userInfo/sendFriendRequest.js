import userInfoPost from "./userInfoPost.js";


export default async(friendAlias) => {
    const data = await userInfoPost('send_friend_request', friendAlias);
    return data;
}