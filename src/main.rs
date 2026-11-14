use std::{env, fs, process::ExitCode};

fn run() -> Result<u8, String> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.is_empty() || matches!(args[0].as_str(), "--help" | "-h") {
        println!("Rig2Print\nUsage: rig2print check-plan <plan.json>\nChecks the design contract, not geometry or printability.\nBlender inspection: python3 -m rig2print inspect --help");
        return Ok(0);
    }
    if args.len() != 2 || args[0] != "check-plan" {
        return Err("expected: rig2print check-plan <plan.json>".into());
    }
    let input = fs::read_to_string(&args[1]).map_err(|error| error.to_string())?;
    let plan = serde_json::from_str(&input).map_err(|error| error.to_string())?;
    let report = rig2print::check_plan(&plan);
    println!("{}", serde_json::to_string_pretty(&report).unwrap());
    Ok(if report["ok"] == true { 0 } else { 1 })
}

fn main() -> ExitCode {
    match run() {
        Ok(code) => ExitCode::from(code),
        Err(message) => {
            eprintln!("rig2print: {message}");
            ExitCode::from(2)
        }
    }
}
