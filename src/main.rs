use std::{
    collections::BTreeMap,
    env, fs,
    io::Write,
    path::{Path, PathBuf},
    process::{Command, ExitCode},
    time::{SystemTime, UNIX_EPOCH},
};

struct AdapterScript(PathBuf);

impl AdapterScript {
    fn create() -> Result<Self, String> {
        let stamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map_err(|error| error.to_string())?
            .as_nanos();
        let path = env::temp_dir().join(format!(
            "rig2print-adapter-{}-{stamp}.py",
            std::process::id()
        ));
        let mut file = fs::OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&path)
            .map_err(|error| error.to_string())?;
        let script = Self(path);
        file.write_all(include_bytes!("../scripts/prototype_joint.py"))
            .map_err(|error| error.to_string())?;
        Ok(script)
    }
}

impl Drop for AdapterScript {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.0);
    }
}

fn prototype(args: &[String]) -> Result<u8, String> {
    if args.first().is_some_and(|arg| arg == "--help") {
        println!("Usage: rig2print prototype-joint <source.blend> --mesh NAME --armature NAME --parent-bone NAME --child-bone NAME --span-mm MM --output-dir DIR [--blender PATH] [--clearance-mm MM] [--wall-mm MM] [--pin-radius-mm MM] [--motion-deg DEGREES]\nExperimental two-body rig-derived hinge specimen; not full-model or print qualification.");
        return Ok(0);
    }
    let source = args
        .first()
        .ok_or("prototype-joint requires a source .blend file")?;
    let mut options: BTreeMap<String, String> = BTreeMap::new();
    let mut rest = args[1..].iter();
    while let Some(key) = rest.next() {
        if !matches!(
            key.as_str(),
            "--mesh"
                | "--armature"
                | "--parent-bone"
                | "--child-bone"
                | "--span-mm"
                | "--output-dir"
                | "--blender"
                | "--clearance-mm"
                | "--wall-mm"
                | "--pin-radius-mm"
                | "--motion-deg"
        ) {
            return Err(format!("unknown prototype option: {key}"));
        }
        let value = rest
            .next()
            .ok_or_else(|| format!("missing value for {key}"))?;
        if options.insert(key.clone(), value.clone()).is_some() {
            return Err(format!("duplicate prototype option: {key}"));
        }
    }
    for key in [
        "--mesh",
        "--armature",
        "--parent-bone",
        "--child-bone",
        "--span-mm",
        "--output-dir",
    ] {
        if !options
            .get(key)
            .is_some_and(|value| !value.trim().is_empty())
        {
            return Err(format!("prototype-joint requires {key}"));
        }
    }
    for key in [
        "--span-mm",
        "--clearance-mm",
        "--wall-mm",
        "--pin-radius-mm",
        "--motion-deg",
    ] {
        if let Some(value) = options.get(key) {
            let number: f64 = value
                .parse()
                .map_err(|_| format!("{key} must be a number"))?;
            if !number.is_finite() || number <= 0.0 || (key == "--motion-deg" && number > 15.0) {
                return Err(format!("{key} is outside the supported positive range"));
            }
        }
    }
    let source = Path::new(source)
        .canonicalize()
        .map_err(|error| error.to_string())?;
    if !source.is_file() || source.extension().and_then(|s| s.to_str()) != Some("blend") {
        return Err("source must be an existing .blend file".into());
    }
    let output = PathBuf::from(&options["--output-dir"]);
    if output.exists() {
        return Err("output directory already exists; choose a new path".into());
    }
    if let Some(parent) = output.parent().filter(|p| !p.as_os_str().is_empty()) {
        fs::create_dir_all(parent).map_err(|error| error.to_string())?;
    }
    fs::create_dir(&output).map_err(|error| error.to_string())?;
    let output = output.canonicalize().map_err(|error| error.to_string())?;
    options.insert("--output-dir".into(), output.to_string_lossy().into());
    let blender = options
        .remove("--blender")
        .unwrap_or_else(|| "blender".into());
    let script = AdapterScript::create()?;
    let mut command = Command::new(blender);
    command
        .args(["--background", "--factory-startup", "--disable-autoexec"])
        .arg(source)
        .args(["--python-exit-code", "1", "--python"])
        .arg(&script.0)
        .arg("--");
    for (key, value) in options {
        command.arg(key).arg(value);
    }
    let status = command
        .status()
        .map_err(|error| format!("could not run Blender: {error}"))?;
    if !status.success() {
        return Err(format!(
            "Blender prototype failed; inspect {} for available evidence",
            output.display()
        ));
    }
    let report: serde_json::Value = serde_json::from_str(
        &fs::read_to_string(output.join("report.json")).map_err(|error| error.to_string())?,
    )
    .map_err(|error| error.to_string())?;
    if report["kind"] != "rig2print-joint-prototype"
        || report["geometry_pass"] != true
        || !output.join("prototype.stl").is_file()
    {
        return Err("Blender did not produce a passing geometry report and STL".into());
    }
    println!(
        "Unprinted joint candidate: {}",
        output.join("prototype.stl").display()
    );
    if report["review_required"] == true {
        println!("Shape review required: inspect preview.png and report.json before printing.");
    }
    Ok(0)
}

fn run() -> Result<u8, String> {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.is_empty() || matches!(args[0].as_str(), "--help" | "-h") {
        println!("Rig2Print\nUsage: rig2print check-plan <plan.json>\n       rig2print prototype-joint --help\nChecks and prototypes are not physical-print qualification.\nBlender inspection: python3 -m rig2print inspect --help");
        return Ok(0);
    }
    if args[0] == "prototype-joint" {
        return prototype(&args[1..]);
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
