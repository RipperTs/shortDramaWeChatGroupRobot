/*
 Navicat Premium Data Transfer

 Source Server         : 抖音话题机器人
 Source Server Type    : MySQL
 Source Server Version : 50740 (5.7.40-log)
 Source Host           : 62.106.70.185:3306
 Source Schema         : douyin_data

 Target Server Type    : MySQL
 Target Server Version : 50740 (5.7.40-log)
 File Encoding         : 65001

 Date: 28/11/2024 08:58:00
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for robot_room
-- ----------------------------
DROP TABLE IF EXISTS `robot_room`;
CREATE TABLE `robot_room` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `room_wxid` varchar(50) DEFAULT '' COMMENT '群 ID',
  `notification_interval` int(11) DEFAULT '10' COMMENT '通知间隔(分钟)',
  `status` tinyint(3) DEFAULT '1',
  `topic_max_num` int(11) DEFAULT '50' COMMENT '最大话题数量',
  `expiration_time` datetime DEFAULT NULL,
  `below_standard` int(11) DEFAULT '30000' COMMENT '通知热度标准值',
  PRIMARY KEY (`id`),
  UNIQUE KEY `robot_room_pk` (`room_wxid`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COMMENT='启用的机器人群';

-- ----------------------------
-- Table structure for robot_room_settings
-- ----------------------------
DROP TABLE IF EXISTS `robot_room_settings`;
CREATE TABLE `robot_room_settings` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `room_wxid` varchar(50) DEFAULT '' COMMENT '微信群的 wxid',
  `admin_wxid` varchar(50) DEFAULT '' COMMENT '管理员 ID',
  `status` tinyint(3) DEFAULT '1' COMMENT ' 启用 1,禁用 0',
  `at_all` tinyint(3) DEFAULT '0' COMMENT '是否允许通知所有人',
  PRIMARY KEY (`id`),
  KEY `robot_room_settings_room_wxid_index` (`room_wxid`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COMMENT='机器人群设置';

-- ----------------------------
-- Table structure for topic_heats
-- ----------------------------
DROP TABLE IF EXISTS `topic_heats`;
CREATE TABLE `topic_heats` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keyword` varchar(50) DEFAULT '' COMMENT '关键字',
  `heat` bigint(20) DEFAULT '0' COMMENT '热度',
  `room_wxid`  varchar(50) default '' null comment '群 ID',
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `topic_heats_keyword_index` (`keyword`)
) ENGINE=InnoDB AUTO_INCREMENT=39576 DEFAULT CHARSET=utf8mb4 COMMENT='话题热度';

-- ----------------------------
-- Table structure for topic_keywords
-- ----------------------------
DROP TABLE IF EXISTS `topic_keywords`;
CREATE TABLE `topic_keywords` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `keyword` varchar(50) DEFAULT '' COMMENT '关键字',
  `status` tinyint(3) DEFAULT '1',
  `shelf_time` datetime DEFAULT NULL COMMENT '预计上架时间',
  `xt_mcn` varchar(50) DEFAULT '' COMMENT '星图MCN',
  `applet` varchar(50) DEFAULT '' COMMENT '小程序融合',
  `theater` varchar(50) DEFAULT '' COMMENT '剧场',
  `television` varchar(50) DEFAULT '' COMMENT '频道',
  `category` varchar(100) DEFAULT '' COMMENT '分类',
  `gf_material_link` varchar(500) DEFAULT '' COMMENT '官方素材链接',
  `other` varchar(255) DEFAULT '' COMMENT '其他',
  `synopsis` varchar(500) DEFAULT '' COMMENT '剧情简介',
  `room_wxid` varchar(50) DEFAULT '' COMMENT '群 ID',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=686 DEFAULT CHARSET=utf8mb4 COMMENT='话题搜索关键词';

SET FOREIGN_KEY_CHECKS = 1;
