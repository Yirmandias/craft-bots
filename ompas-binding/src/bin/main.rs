use std::fs;
//use ompas_gobotsim::mod_godot::CtxGodot;
use ompas_binding::{PlatformCraftBots, DEFAULT_CRAFT_BOTS_PATH};
use ompas_middleware::logger::{FileDescriptor, LogClient};
use ompas_middleware::{LogLevel, Master};
use ompas_rae_core::monitor::CtxRaeUser;
use ompas_rae_interface::platform::Domain;
use ompas_rae_interface::{LOG_TOPIC_PLATFORM, PLATFORM_CLIENT};
use sompas_modules::advanced_math::CtxMath;
use sompas_modules::io::CtxIo;
use sompas_modules::string::CtxString;
use sompas_modules::utils::CtxUtils;
use sompas_repl::lisp_interpreter::{LispInterpreter, LispInterpreterConfig};
use std::path::PathBuf;
use structopt::StructOpt;

pub const TOKIO_CHANNEL_SIZE: usize = 100;
const LOG_LEVEL: LogLevel = LogLevel::Debug;

#[derive(Debug, StructOpt)]
#[structopt(name = "OMPAS", about = "An acting engine based on RAE.")]
struct Opt {
    #[structopt(short = "d", long = "debug")]
    debug: bool,
    #[structopt(short = "p", long = "log-path")]
    log: Option<PathBuf>,
    #[structopt(short = "r", long = "rae-log")]
    rae_log: bool,
}

#[tokio::main]
async fn main() {
    println!("OMPAS v0.1");

    let opt: Opt = Opt::from_args();
    println!("{:?}", opt);
    Master::set_log_level(LOG_LEVEL).await;
    if opt.debug {
        Master::set_log_level(LogLevel::Trace).await;
    }
    //test_lib_model(&opt);
    lisp_interpreter(opt.log, opt.rae_log).await;
}

pub async fn lisp_interpreter(log: Option<PathBuf>, _: bool) {
    let mut li = LispInterpreter::new().await;

    let mut ctx_io = CtxIo::default();
    let ctx_math = CtxMath::default();
    let ctx_utils = CtxUtils::default();
    let ctx_string = CtxString::default();

    //Insert the doc for the different contexts.

    //Add the sender of the channel.
    if let Some(pb) = &log {
        ctx_io.set_log_output(pb.clone().into());
    }

    li.import_namespace(ctx_utils);
    li.import_namespace(ctx_io);
    li.import_namespace(ctx_math);
    li.import(ctx_string);

    let ctx_rae = CtxRaeUser::new(
        PlatformCraftBots::new(
            Domain::File(
                "/home/jeremy/CLionProjects/ompas/craft-bots/ompas-binding/domain/domain.lisp"
                    .into(),
            ),
            LogClient::new(PLATFORM_CLIENT, LOG_TOPIC_PLATFORM).await,
            DEFAULT_CRAFT_BOTS_PATH.parse().unwrap(),
        )
        .await,
        log.clone(),
        true,
    )
    .await;
    li.import_namespace(ctx_rae);

    li.set_config(LispInterpreterConfig::new(true));

    li.run(log.map(|p| FileDescriptor::AbsolutePath(fs::canonicalize(p).unwrap())))
        .await;
    Master::end().await;
}
