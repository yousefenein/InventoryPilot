"use client";

import type {CardProps} from "@heroui/react";
import React, { useEffect, useState } from "react";
import {
  Button,
  Card,
  CardBody,
  CardHeader,
  Chip,
  Tabs,
  Tab,
  ScrollShadow,
  CardFooter,
  Switch,
  Popover,
  PopoverTrigger,
  PopoverContent,
} from "@heroui/react";
import {Icon} from "@iconify/react";
import NotificationItem from "./notification-item";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

type Notification = {
  id: string;
  isRead?: boolean;
  avatar: string;
  description: string;
  name: string;
  time: string;
  type?: "default" | "request" | "file";
};

enum NotificationTabs {
  All = "all",
  Unread = "unread",
  Archive = "archive",
}

const fetchNotifications = async () => {
  const response = await fetch(`${API_BASE_URL}/orders/delayed_orders`);
  const data = await response.json();
  return data.map((order: any) => ({
    id: order.order_id,
    isRead: false,
    description: `Order ${order.order_id} is ${order.delay} days over due.`,
    name: "Notification System",
    time: new Date().toLocaleString(),
    type: "default",
  }));
};

export default function DelayedOrdersNotifCard(props: CardProps & { onMarkAllAsRead?: () => void }) {
  const [activeTab, setActiveTab] = React.useState<NotificationTabs>(NotificationTabs.All);
  const [delayedOrdersNotifications, setDelayedOrdersNotifications] = useState<Notification[]>([]);
  const [archivedNotifications, setArchivedNotifications] = useState<Notification[]>([]);
  const [isSubscribed, setIsSubscribed] = useState(true);

  useEffect(() => {
    const loadDelayedOrdersNotifications = async () => {
      try {
        const storedNotifications = localStorage.getItem("delayedOrdersNotifications");
        if (storedNotifications) {
          setDelayedOrdersNotifications(JSON.parse(storedNotifications));
        } else {
          const data = await fetchNotifications();
          setDelayedOrdersNotifications(data);
          localStorage.setItem("delayedOrdersNotifications", JSON.stringify(data));
        }
      } catch (error) {
        console.error("Error fetching low stock notifications:", error);
      }
    };

    loadDelayedOrdersNotifications();
  }, []);

  const markAllAsRead = () => {
    setDelayedOrdersNotifications((prevNotifications) => {
      const updatedNotifications = prevNotifications.map((notification) => ({ ...notification, isRead: true }));
      localStorage.setItem("delayedOrdersNotifications", JSON.stringify(updatedNotifications));
      if (props.onMarkAllAsRead) {
        props.onMarkAllAsRead();
      }
      return updatedNotifications;
    });
  };

  const markAsRead = (id: string) => {
    setDelayedOrdersNotifications((prevNotifications) => {
      const updatedNotifications = prevNotifications.map((notification) =>
        notification.id === id ? { ...notification, isRead: true } : notification
      );
      localStorage.setItem("delayedOrdersNotifications", JSON.stringify(updatedNotifications));
      return updatedNotifications;
    });
  };

  const archiveAll = () => {
    setArchivedNotifications((prevArchived) => {
      const updatedArchived = [...prevArchived, ...delayedOrdersNotifications];
      localStorage.setItem("archivedNotifications", JSON.stringify(updatedArchived));
      return updatedArchived;
    });
    setDelayedOrdersNotifications([]);
    localStorage.removeItem("delayedOrdersNotifications");
  };

  const allNotifications = delayedOrdersNotifications;
  const unreadNotifications = delayedOrdersNotifications.filter(notification => !notification.isRead);

  const activeNotifications = activeTab === NotificationTabs.All ? allNotifications : unreadNotifications;
  const archiveNotifications = activeTab === NotificationTabs.Archive ? archivedNotifications : [];

  const toggleSubscription = () => {
    setIsSubscribed(!isSubscribed);
  };

  const [settingsVisible, setSettingsVisible] = useState(false);
  return (
    <div className="flex items-center justify-center">
      <Card className="w-full max-w-[420px]" {...props}>
        <CardHeader className="flex flex-col px-0 pb-0">
          <div className="flex w-full items-center justify-between px-5 py-2">
            <div className="inline-flex items-center gap-1">
              <h4 className="inline-block align-middle text-large font-medium">Notifications</h4>
              <Chip size="sm" variant="flat">
                {activeTab === NotificationTabs.Archive ? archiveNotifications.length : activeNotifications.length}
              </Chip>
            </div>
            <Button className="h-8 px-3" color="primary" radius="full" variant="light" onClick={markAllAsRead}>
              Mark all as read
            </Button>
          </div>
          <Tabs
            aria-label="Notifications"
            classNames={{
              base: "w-full",
              tabList: "gap-6 px-6 py-0 w-full relative rounded-none border-b border-divider",
              cursor: "w-full",
              tab: "max-w-fit px-2 h-12",
            }}
            color="primary"
            selectedKey={activeTab}
            variant="underlined"
            onSelectionChange={(selected) => setActiveTab(selected as NotificationTabs)}
          >
            <Tab
              key="all"
              title={
                <div className="flex items-center space-x-2">
                  <span>All</span>
                  <Chip size="sm" variant="flat">
                    {allNotifications.length}
                  </Chip>
                </div>
              }
            />
            <Tab
              key="unread"
              title={
                <div className="flex items-center space-x-2">
                  <span>Unread</span>
                  <Chip size="sm" variant="flat">
                    {unreadNotifications.length}
                  </Chip>
                </div>
              }
            />
            <Tab
              key="archive"
              title={
                <div className="flex items-center space-x-2">
                  <span>Archive</span>
                  <Chip size="sm" variant="flat">
                    {archiveNotifications.length}
                  </Chip>
                </div>
              }
            />
          </Tabs>
        </CardHeader>
        <CardBody className="w-full gap-0 p-0">
          <ScrollShadow className="h-[500px] w-full">
            {activeTab === NotificationTabs.Archive ? (
              archiveNotifications.length > 0 ? (
                archiveNotifications.map((notification) => (
                  <NotificationItem key={notification.id} {...notification} />
                ))
              ) : (
                <div className="flex h-full w-full flex-col items-center justify-center gap-2">
                  <Icon className="text-default-400" icon="solar:bell-off-linear" width={40} />
                  <p className="text-small text-default-400">No archived notifications yet.</p>
                </div>
              )
            ) : activeNotifications.length > 0 ? (
              activeNotifications.map((notification) => (
                <NotificationItem key={notification.id} {...notification} onClick={() => markAsRead(notification.id)} />
              ))
            ) : (
              <div className="flex h-full w-full flex-col items-center justify-center gap-2">
                <Icon className="text-default-400" icon="solar:bell-off-linear" width={40} />
                <p className="text-small text-default-400">No notifications yet.</p>
              </div>
            )}
          </ScrollShadow>
        </CardBody>
        <CardFooter className="justify-end gap-2 px-4">
          <Popover>
            <PopoverTrigger>
              <Button variant={activeTab === NotificationTabs.Archive ? "flat" : "light"}>
                Settings
              </Button>
            </PopoverTrigger>
            <PopoverContent>
              <Card>
                <CardHeader>
                  <h4 className="text-large font-medium">Settings</h4>
                </CardHeader>
                <CardBody>
                  <div className="flex items-center justify-between gap-4">
                    <span>Subscribe to email notifications</span>
                    <Switch checked={isSubscribed} onChange={toggleSubscription} />
                  </div>
                </CardBody>
              </Card>
            </PopoverContent>
          </Popover>
          {activeTab !== NotificationTabs.Archive && (
            <Button variant="flat" onClick={archiveAll}>
              Archive All
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}
