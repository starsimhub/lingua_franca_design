-- Links to a folder work on GitHub, which shows the folder's README. On the site they
-- need a page, so point them at the folder's summary (index.qmd) if it has one, or its README.

local function exists(path)
  local file = io.open(path, 'r')
  if file then file:close() end
  return file ~= nil
end

function Link(link)
  local target = link.target
  if target:match('^%a[%w+.-]*:') or target:match('^[#/]') then return nil end -- A URL, an anchor, or a path from the root
  local path, anchor = target:match('^([^#]*)(.*)$')
  local last = path:gsub('/+$', ''):match('([^/]*)$')
  if last:match('%.%w+$') and last ~= '..' then return nil end -- A file, not a folder
  local folder = pandoc.path.join({pandoc.path.directory(quarto.doc.input_file), path})
  for _, name in ipairs({'index.qmd', 'README.md'}) do
    if exists(pandoc.path.join({folder, name})) then
      link.target = pandoc.path.join({path, name}) .. anchor
      return link
    end
  end
end
