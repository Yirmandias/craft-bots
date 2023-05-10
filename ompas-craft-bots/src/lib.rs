use async_trait::async_trait;
use ompas_core::ompas::manager::state::world_state::WorldStateSnapshot;
use ompas_core::ompas::scheme::exec::platform::lisp_domain::LispDomain;
use ompas_core::ompas::scheme::exec::platform::platform_config::{
    InnerPlatformConfig, PlatformConfig,
};
use ompas_core::ompas::scheme::exec::platform::PlatformDescriptor;
use ompas_core::ompas::scheme::exec::state::ModState;
use ompas_language::exec::state::MOD_STATE;
use ompas_language::interface::{
    DEFAULT_PLATFORM_SERVICE_IP, DEFAULT_PLATFROM_SERVICE_PORT, LOG_TOPIC_PLATFORM,
    PROCESS_TOPIC_PLATFORM,
};
use ompas_middleware::logger::LogClient;
use ompas_middleware::{Master, ProcessInterface};
use sompas_macros::async_scheme_fn;
use sompas_structs::lenv::LEnv;
use sompas_structs::lmodule::LModule;
use sompas_structs::lruntimeerror::LRuntimeError;
use sompas_structs::lvalues::LValueS;
use std::collections::{HashMap, HashSet};
use std::fmt::{Display, Formatter};
use std::fs::File;
use std::net::SocketAddr;
use std::os::unix::io::{FromRawFd, IntoRawFd};
use std::path::PathBuf;
use std::process::{Command, Stdio};
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::RwLock;
use tokio::time::sleep;

//const TOKIO_CHANNEL_SIZE: usize = 100;
const PROCESS_CRAFT_BOTS: &str = "__PROCESS_CRAFT_BOTS_SIM__";
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
    pub domain: LispDomain,
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
            domain: LispDomain::default(),
            config: CraftBotsConfig {
                path: DEFAULT_CRAFT_BOTS_PATH.into(),
            },
            log: Default::default(),
        }
    }
}

impl PlatformCraftBots {
    pub async fn new(domain: LispDomain, log: LogClient, path: PathBuf) -> Self {
        Master::set_child_process(PROCESS_TOPIC_PLATFORM, PROCESS_TOPIC_CRAFT_BOTS).await;
        Master::set_child_process(PROCESS_TOPIC_CRAFT_BOTS, PROCESS_TOPIC_PLATFORM).await;
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

        let f1 = File::create("craft-bots-out.txt").expect("couldn't create file");
        let f2 = File::create("craft-bots-err.txt").expect("couldn't create file");

        let path = config
            .path
            .canonicalize()
            .unwrap()
            .to_str()
            .unwrap()
            .to_string();
        //println!("craft-bots path = {path}");
        //self.log.debug(format!("craft-bots path = {path}"));

        let mut child = Command::new("python3")
            .current_dir(path)
            .args(["main.py"])
            .stdin(Stdio::null())
            .stdout(unsafe { Stdio::from_raw_fd(f1.into_raw_fd()) })
            .stderr(unsafe { Stdio::from_raw_fd(f2.into_raw_fd()) })
            .spawn()
            .expect("failed to execute process");

        let mut process = ProcessInterface::new(
            PROCESS_CRAFT_BOTS,
            PROCESS_TOPIC_CRAFT_BOTS,
            LOG_TOPIC_PLATFORM,
        )
        .await;

        tokio::spawn(async move {
            //blocked on the reception of the end signal.
            process.recv().await.expect("error receiving kill message");
            child.kill().expect("could not kill godot");
        });
        sleep(Duration::from_millis(1000)).await;

        self.log.info("Successfully started platform.").await;
    }

    async fn stop(&self) {
        self.log
            .info("Process Craft-Bots killed via subscriptions of its different processes.")
            .await;
    }

    async fn domain(&self) -> LispDomain {
        self.domain.clone()
    }

    async fn module(&self) -> Option<LModule> {
        Some(CraftBotsModule::default().into())
    }

    async fn socket(&self) -> SocketAddr {
        self.service_info
    }
}

pub type Node = String;

pub type NodeId = usize;

pub struct Edge {
    node_a: NodeId,
    node_b: NodeId,
    weight: i64,
}

#[derive(Default)]
pub struct Graph {
    nodes_ids: HashMap<Node, NodeId>,
    nodes: HashMap<NodeId, Node>,
    edges: Vec<Edge>,
    n_nodes: usize,
}

#[derive(Default)]
struct CraftBotsModule {
    graph: Arc<RwLock<Graph>>,
}

impl CraftBotsModule {
    async fn add_new_edge(&self, node_a: Node, node_b: Node, weight: i64) {
        let mut graph = self.graph.write().await;
        let node_a_id = graph.nodes_ids.get(&node_a).cloned();
        let node_a_id = match node_a_id {
            None => {
                let id = graph.n_nodes;
                graph.nodes_ids.insert(node_a.to_string(), id);
                graph.nodes.insert(id, node_a.to_string());
                graph.n_nodes += 1;
                id
            }
            Some(id) => id,
        };

        let node_b_id = graph.nodes_ids.get(&node_b).cloned();
        let node_b_id = match node_b_id {
            None => {
                let id = graph.n_nodes;
                graph.nodes_ids.insert(node_b.to_string(), id);
                graph.nodes.insert(id, node_b.to_string());
                graph.n_nodes += 1;
                id
            }
            Some(id) => id,
        };

        graph.edges.push(Edge {
            node_a: node_a_id,
            node_b: node_b_id,
            weight,
        });
    }
    /// Update the graph in function of the context
    /// Used just before calling dijkstra
    async fn update_graph(&self, world_state: WorldStateSnapshot) {
        let edges: Vec<String> = world_state.instance.get_instances("edge");
        for edge in edges {
            let edge: LValueS = edge.into();

            let key_node_a: Vec<LValueS> = vec!["edge.node_a".into(), edge.clone()];
            let node_a = world_state
                .r#static
                .get(&LValueS::from(key_node_a))
                .unwrap();
            let key_node_b: Vec<LValueS> = vec!["edge.node_b".into(), edge.clone()];
            let node_b = world_state
                .r#static
                .get(&LValueS::from(key_node_b))
                .unwrap();
            let weight: i64 = world_state
                .r#static
                .get(&LValueS::from(vec![LValueS::from("edge.length"), edge]))
                .unwrap()
                .try_into()
                .unwrap();
            self.add_new_edge(node_a.to_string(), node_b.to_string(), weight)
                .await;
        }
    }

    /// Return a sequence of node to go from node_start to node_end
    async fn dijkstra(&self, node_start: Node, node_end: Node) -> Vec<Node> {
        let graph = self.graph.read().await;

        let sstart = *graph.nodes_ids.get(&node_start).unwrap();
        let send = *graph.nodes_ids.get(&node_end).unwrap();
        let mut distances: Vec<Option<i64>> = vec![None; graph.n_nodes];
        distances[sstart] = Some(0);

        let mut weights: Vec<Vec<Option<i64>>> = vec![vec![None; graph.n_nodes]; graph.n_nodes];
        let mut neighbours: Vec<Vec<NodeId>> = vec![vec![]; graph.n_nodes];

        for edge in &graph.edges {
            weights[edge.node_a][edge.node_b] = Some(edge.weight);
            weights[edge.node_b][edge.node_a] = Some(edge.weight);
            neighbours[edge.node_a].push(edge.node_b);
            neighbours[edge.node_b].push(edge.node_a);
        }

        let mut predecessors: Vec<Option<NodeId>> = vec![None; graph.n_nodes];

        /*let find_min = |queue: &HashSet<NodeId>| -> Option<NodeId> {
            let mut mini = None;
            let mut top: Option<NodeId> = None;
            for node in queue {
                match mini {
                    None => mini = distances[*node].clone(),
                    Some(v) => {
                        if let Some(distance) = distances[*node] {
                            if distance < v {
                                mini = Some(distance);
                                top = Some(*node)
                            }
                        }
                    }
                }
            }
            top
        };*/

        /*let mut maj_distances = |s1: &NodeId, s2: &NodeId| {
            let distance_s1 = distances[*s1].clone();
            let distance_s2 = distances[*s2].clone();
            let weight = weights[*s1][*s2].unwrap();

            match (distance_s2, distance_s1) {
                (None, Some(d1)) => {
                    distances[*s2] = Some(d1 + weight);
                    predecessors[*s2] = Some(*s1);
                }
                (Some(d2), Some(d1)) => {
                    if d2 > d1 + weight {
                        distances[*s2] = Some(d1 + weight);
                        predecessors[*s2] = Some(*s1);
                    }
                }
                _ => {}
            }
        };*/

        let mut queue: HashSet<NodeId> = HashSet::default();
        for id in 0..graph.n_nodes {
            queue.insert(id);
        }

        while !queue.is_empty() {
            //Find min
            let s1 = {
                let mut mini = None;
                let mut top: Option<NodeId> = None;
                for node in &queue {
                    match mini {
                        None => {
                            mini = distances[*node];
                            top = Some(*node);
                        }
                        Some(v) => {
                            if let Some(distance) = distances[*node] {
                                if distance < v {
                                    mini = Some(distance);
                                    top = Some(*node)
                                }
                            }
                        }
                    }
                }
                top.unwrap()
            };
            queue.remove(&s1);
            for s2 in &neighbours[s1] {
                //MAJ DISTANCE
                let distance_s1 = distances[s1];
                let distance_s2 = distances[*s2];
                let weight = weights[s1][*s2].unwrap();

                match (distance_s2, distance_s1) {
                    (None, Some(d1)) => {
                        distances[*s2] = Some(d1 + weight);
                        predecessors[*s2] = Some(s1);
                    }
                    (Some(d2), Some(d1)) => {
                        if d2 > d1 + weight {
                            distances[*s2] = Some(d1 + weight);
                            predecessors[*s2] = Some(s1);
                        }
                    }
                    _ => {}
                }
            }
        }

        let mut route = vec![];
        let mut s = send;
        while s != sstart {
            route.push(s);
            s = predecessors[s].unwrap();
        }

        route.reverse();

        route
            .drain(..)
            .map(|n| graph.nodes.get(&n).unwrap().clone())
            .collect()
    }
}

#[async_scheme_fn]
pub async fn find_route(
    env: &LEnv,
    node_a: Node,
    node_b: Node,
) -> Result<Vec<Node>, LRuntimeError> {
    let ctx = env.get_context::<CraftBotsModule>(CRAFT_BOTS_MOD)?;
    let ctx_state = env.get_context::<ModState>(MOD_STATE)?;

    ctx.update_graph(ctx_state.state.get_snapshot().await).await;

    Ok(ctx.dijkstra(node_a, node_b).await)
}

pub const CRAFT_BOTS_MOD: &str = "craft-bots-mod";
pub const FIND_ROUTE: &str = "find_route";

impl From<CraftBotsModule> for LModule {
    fn from(m: CraftBotsModule) -> Self {
        let mut module = LModule::new(m, "cbm", "");
        module.add_async_fn(FIND_ROUTE, find_route, "", false);
        module
    }
}
