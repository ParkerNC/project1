use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

struct TLB {
    set_num: u16,
    ass: u16,
    active: bool,
    cache: Vec<i32>,
}

struct PT {
    physical_page_num: u16,
    virtual_page_num: u16,
    active: bool,
    cache: Vec<i32>,
}

struct DC {
    set_num: u16,
    ass: u16,
    block_size: u16,
    write_back: bool,
    cache: Vec<i32>,
}

struct L2 {
    set_num: u16,
    ass: u16,
    block_size: u16,
    write_back: bool,
    active: bool,
    cache: Vec<i32>,
}

fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where P: AsRef<Path>, {
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}

fn main() {

    let mut tlb: TLB = TLB {
        set_num: 256,
        ass: 8,
        active: true,
        cache: Vec::new(),
    };

    let mut pt: PT = PT {
        physical_page_num: 1024,
        virtual_page_num: 8192,
        active: true,
        cache: Vec::new(),
    };

    let mut dc: DC = DC {
        set_num: 8192,
        ass: 8,
        block_size: 8,
        write_back: true,
        cache: Vec::new(),
    };

    let mut l2: L2 = L2 {
        set_num: 8192,
        ass: 8,
        block_size: 8,
        write_back: true,
        active: true,
        cache: Vec::new(),
    };

    let mut config_lines = Vec::<String>::new();
    //read config and establish cache values
    if let Ok(lines) = read_lines("./trace.config") {
        for line in lines {
            if let Ok(option) = line {
                config_lines.push(option);
            }
        }
    }
    
    for x in 0..config_lines.len()-1{
        if config_lines[x].contains("Data TLB configuration") {
            println!("{}", config_lines[x]);
        }
        else if config_lines[x].contains("Page Table configuration") {
            println!("{}", config_lines[x]);
        }
        else if config_lines[x].contains("Data Cache configuration") {
            println!("{}", config_lines[x]);
        }
        else if config_lines[x].contains("L2 Cache configuration") {
            println!("{}", config_lines[x]);
        }
        else if config_lines[x].contains("Virtual addresses: y") {
            println!("{}", config_lines[x]);
        }
        else if config_lines[x].contains("TLB:") {
            println!("{}", config_lines[x]);
        }
        else if config_lines[x].contains("L2 cache:") {
            println!("{}", config_lines[x]);
        }
    }
}

