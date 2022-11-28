use async_trait::async_trait;
use ompas_middleware::logger::LogClient;
use ompas_middleware::ProcessInterface;
use ompas_rae_interface::platform::{
    Domain, InnerPlatformConfig, PlatformConfig, PlatformDescriptor, PlatformModule,
};
use ompas_rae_interface::{
    DEFAULT_PLATFORM_SERVICE_IP, DEFAULT_PLATFROM_SERVICE_PORT, LOG_TOPIC_PLATFORM,
    PROCESS_TOPIC_PLATFORM,
};
use std::env::set_current_dir;
use std::fmt::{Display, Formatter};
use std::fs::File;
use std::net::SocketAddr;
use std::os::unix::io::{FromRawFd, IntoRawFd};
use std::path::PathBuf;
use std::process::{Command, Stdio};
use std::time::Duration;
use tokio::time::sleep;

const TOKIO_CHANNEL_SIZE: usize = 100;
const PROCESS_CRAFTBOTS: &str = "__PROCESS_GOBOT_SIM__";
const PROCESS_SERVER_GRPC: &str = "__PROCESS_SERVER_GRPC__";
pub const DEFAULT_CRAFT_BOTS_PATH: &str = "/home/jeremy/CLionProjects/ompas/craft-bots";
const PROCESS_TOPIC_CRAFT_BOTS: &str = "__PROCESS_TOPIC_CRAFT_BOTS__";

#[derive(Clone)]
pub struct CraftBotsConfig {
    path: PathBuf,
}

impl Display for CraftBotsConfig {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        write!(f, "--path {}", self.path.to_str().unwrap())
    }
}

impl From<String> for CraftBotsConfig {
    fn from(s: String) -> Self {
        let mut args = s.split_whitespace();
        let mut path: PathBuf = DEFAULT_CRAFT_BOTS_PATH.parse().unwrap();
        while let Some(arg) = args.next() {
            if arg == "--path" {
                path = args.next().unwrap().parse().unwrap();
                break;
            }
        }
        Self { path }
    }
}

pub struct PlatformCraftBots {
    pub service_info: SocketAddr,
    pub domain: Domain,
    pub config: CraftBotsConfig,
    pub log: LogClient,
}

impl Default for PlatformCraftBots {
    fn default() -> Self {
        Self {
            service_info: format!(
                "{}:{}",
                DEFAULT_PLATFORM_SERVICE_IP, DEFAULT_PLATFROM_SERVICE_PORT
            )
            .parse()
            .unwrap(),
            domain: Domain::default(),
            config: CraftBotsConfig {
                path: DEFAULT_CRAFT_BOTS_PATH.into(),
            },
            log: Default::default(),
        }
    }
}

impl PlatformCraftBots {
    pub fn new(domain: Domain, log: LogClient, path: PathBuf) -> Self {
        PlatformCraftBots {
            service_info: format!(
                "{}:{}",
                DEFAULT_PLATFORM_SERVICE_IP, DEFAULT_PLATFROM_SERVICE_PORT
            )
            .parse()
            .unwrap(),
            domain,
            config: CraftBotsConfig { path },
            log,
        }
    }

    pub fn set_server_info(&mut self, socket_info: SocketAddr) {
        self.service_info = socket_info;
    }

    pub fn get_server_info(&self) -> &SocketAddr {
        &self.service_info
    }
}

#[async_trait]
impl PlatformDescriptor for PlatformCraftBots {
    async fn start(&self, config: PlatformConfig) {
        let config: CraftBotsConfig = match config.get_inner::<CraftBotsConfig>() {
            InnerPlatformConfig::String(s) => s.to_string().into(),
            InnerPlatformConfig::Any(s) => s.clone(),
            InnerPlatformConfig::None => self.config.clone(),
        };

        let f1 = File::create("craft-bots.txt").expect("couldn't create file");
        let f2 = File::create("craft-bots.txt").expect("couldn't create file");

        let path = config
            .path
            .canonicalize()
            .unwrap()
            .to_str()
            .unwrap()
            .to_string();
        println!("craft-bots path = {path}");
        //self.log.debug(format!("craft-bots path = {path}"));
        //let command = format!("cd {path} ; python3 main.py");
        set_current_dir(path).unwrap();
        //println!("command = {command}");
        let mut child = Command::new("python3")
            .args(&["main.py"])
            .stdout(unsafe { Stdio::from_raw_fd(f1.into_raw_fd()) })
            .stderr(unsafe { Stdio::from_raw_fd(f2.into_raw_fd()) })
            .spawn()
            .expect("failed to execute process");

        let mut process = ProcessInterface::new(
            PROCESS_CRAFTBOTS,
            PROCESS_TOPIC_CRAFT_BOTS,
            LOG_TOPIC_PLATFORM,
        )
        .await;

        tokio::spawn(async move {
            //blocked on the reception of the end signal.
            process.recv().await.expect("error receiving kill message");
            child.kill().expect("could not kill godot");
        });
        sleep(Duration::from_secs(100)).await;

        self.log.info("Successfully started platform.").await;
    }

    async fn stop(&self) {
        panic!("Not implemented yet")
    }

    async fn domain(&self) -> Domain {
        self.domain.clone()
    }

    async fn module(&self) -> Option<PlatformModule> {
        None
    }

    async fn socket(&self) -> SocketAddr {
        self.service_info.clone()
    }
}
