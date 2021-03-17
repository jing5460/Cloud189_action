# 启用消息推送
目前支持推送的平台:
> 可同时启用多个平台的推送功能
- [钉钉群组机器人](#配置钉钉群组机器人消息推送)
- [PushPlus](#配置-pushplus-消息推送)



## 配置钉钉群组机器人消息推送
1. 使用钉钉 PC 端打开目标群, 或新建一个群组
2. 在该群中打开设置 `智能群助手->添加机器人->自定义机器人`
3. 安全设置选择 `加签`, 并复制出签名秘钥
4. 打开 Github 设置参数 ([参照教程](deploy.md#二设置账号密码))
    ```text
    Name: DINGTALK_SECRET
    Value: 上一步所复制的值
    ```
5. 点击完成, 并设置 `DINGTALK_WEBHOOK` 参数
    ```text
        Name: DINGTALK_WEBHOOK
        Value: 客户端所示的值
    ```
6. 钉钉群组机器人推送消息配置完成


## 配置 PushPlus 消息推送
1. 打开 [PushPlus 官网](http://pushplus.plus/)
2. 使用微信扫码登录, 并复制 token
3. 打开 Github 设置参数 ([参照教程](deploy.md#二设置账号密码))
    ```text
    Name: PUSHPLUS_TOKEN
    Value: 上一步所复制的值
    ```
4. PushPlus 推送消息配置完成