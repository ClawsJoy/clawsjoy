class ClawsJoySanitizer {
  constructor() {
    this.patterns = {
      phone: /1[3-9]\d{9}/g,
      idCard: /\d{17}[\dXx]/g,
      email: /\S+@\S+\.\S+/g
    };
  }
  
  sanitize(text) {
    let redacted = text;
    const stats = {};
    
    for (const [name, pattern] of Object.entries(this.patterns)) {
      const matches = redacted.match(pattern);
      if (matches) {
        stats[name] = matches.length;
        redacted = redacted.replace(pattern, `[${name}]`);
      }
    }
    
    return { redacted, stats };
  }
}

module.exports = ClawsJoySanitizer;
