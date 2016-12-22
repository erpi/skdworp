---
# http://www.grall.name/posts/1/antiSpam-emailAddressObfuscation.html
# http://www.grall.name/posts/1/onlineTools_obfuscation.html
---

function decrypt(origin, size, key, word) {
  var s = 0
  for (var i = 0; i < key.length; i++) {
    s = s + key.charCodeAt(i)
  }
  var pos = 0
  var first = s % word.length
  var prefix = ''
  var suffix = ''
  for (var i = 0; i < word.length - first; i++) {
    suffix = suffix + String.fromCharCode((word.charCodeAt(i) + size - key.charCodeAt(pos)) % size+ origin)
    pos = (pos + 1) % key.length
  }
  for (var i = word.length - first; i < word.length; i++) {
    prefix = prefix + String.fromCharCode((word.charCodeAt(i) + size - key.charCodeAt(pos)) % size + origin)
    pos = (pos + 1) % key.length
  }
  var d = prefix + suffix
  return d;
}
