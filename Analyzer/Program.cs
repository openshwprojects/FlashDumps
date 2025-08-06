using System;
using System.IO;
using System.Text;
using System.Collections.Generic;

class Program
{
    static void Main()
    {
        string repoRoot = Directory.GetCurrentDirectory();
        //repoRoot = "E:/GIT/FlashDumps";
        string[] binFiles = Directory.GetFiles(repoRoot, "*.bin", SearchOption.AllDirectories);
        List<string> filtered = new List<string>();

        foreach (string file in binFiles)
        {
            string rel = file.Replace(repoRoot + Path.DirectorySeparatorChar, "").Replace("\\", "/");
            if (rel.StartsWith("IoT/BK"))
            {
                filtered.Add(rel);
            }
        }
        StringBuilder sb = new StringBuilder();
        sb.AppendLine("<html><body><h1>BIN File Index</h1><ul>");
        foreach (string f in filtered)
        {
            sb.AppendFormat("<li><a href=\"{0}\">{0}</a></li>\n", f);
        }
        sb.AppendLine("</ul></body></html>");

        Directory.CreateDirectory("output");
        File.WriteAllText("output/index.html", sb.ToString());
    }
}
