package com.platform.message.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import java.util.Map;

/**
 * 通知服务
 *
 * @author Platform Team
 * @since 1.0.0
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class NotificationService {

    private final SimpMessagingTemplate messagingTemplate;

    /**
     * 发送广播消息
     */
    public void broadcast(String destination, Object message) {
        messagingTemplate.convertAndSend("/topic/" + destination, message);
        log.info("发送广播消息: destination={}, message={}", destination, message);
    }

    /**
     * 发送点对点消息
     */
    public void sendToUser(String userId, String destination, Object message) {
        messagingTemplate.convertAndSendToUser(userId, "/queue/" + destination, message);
        log.info("发送点对点消息: userId={}, destination={}, message={}", userId, destination, message);
    }

    /**
     * 发送系统通知
     */
    public void sendSystemNotification(String title, String content) {
        Map<String, Object> notification = Map.of(
                "type", "system",
                "title", title,
                "content", content,
                "timestamp", System.currentTimeMillis()
        );
        broadcast("notifications", notification);
    }

    /**
     * 发送用户通知
     */
    public void sendUserNotification(String userId, String title, String content) {
        Map<String, Object> notification = Map.of(
                "type", "user",
                "title", title,
                "content", content,
                "timestamp", System.currentTimeMillis()
        );
        sendToUser(userId, "notifications", notification);
    }
}
