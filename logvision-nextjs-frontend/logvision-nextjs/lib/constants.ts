export const APPLICATIONS = ["MegaCash", "MegaCor", "MegaCommon", "MegaCustody"] as const;
export type ApplicationKey = (typeof APPLICATIONS)[number];
export const COMPONENTS_BY_APP: Record<ApplicationKey, string[]> = {
  MegaCash: ["Persistence", "MegaCashSLALogger", "MegaCashGetLazy", "MegaCashmapping", "MegaBroker", "MegaCashCacheViewLog", "EasyTest", "ExportImportConfig", "IODevices", "LifeCycleLog", "logInit", "Default", "BasicStruct", "BroadcastLogger"],
  MegaCor: ["Persistence", "QuartzScheduler", "MegaCorSLALogger", "MegaBroker", "MegaCorCacheViewLog", "MegaCorGetLazy", "MegaCormapping", "MegaCorNotification", "Default", "EasyTest", "ExportImportConfig", "IODevices", "LifeCycleLog", "logInit", "BasicStruct", "BroadcastLogger", "DCLogger"],
  MegaCommon: ["UploadedFiles", "QuartzScheduler", "Persistence", "MegaCommonSLALogger", "MegaCommonmapping", "MegaBroker", "MegaCommonCacheViewLog", "MegaCommonGetLazy", "IODevices", "LifeCycleLog", "logInit", "Default", "EasyTest", "ExportImportConfig", "BroadcastLogger", "BasicStruct"],
  MegaCustody: ["Persistence", "QuartzScheduler", "SLALogger", "MegaCustodymapping", "MegaCustodySLALogger", "MegaBroker", "MegaCustodyCacheViewLog", "MegaCustodyGetLazy", "LifeCycleLog", "logInit", "Default", "EasyTest", "ExportImportConfig", "IODevices", "BasicStruct", "BroadcastLogger"],
};
