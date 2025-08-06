using System;
using System.IO;
using System.Text;
using System.Collections.Generic;

class Program
{
    static void Main()
    {
        string root = Directory.GetCurrentDirectory();
        string[] files = Directory.GetFiles(Path.Combine(root, ".."), "*.bin", SearchOption.AllDirectories);
        List<string> list = new List<string>();

        foreach (string file in files)
        {
            string rel = file.Replace(root + "/../", "").Replace("\\", "/");
            if (rel.StartsWith("IoT/BK"))
                list.Add(rel);
        }

        StringBuilder sb = new StringBuilder();
        sb.AppendLine("<html><body><h1>BIN File Index</h1><ul>");
        foreach (string f in list)
            sb.AppendFormat("<li><a href=\"{0}\">{0}</a></li>\n", f);
        sb.AppendLine("</ul></body></html>");

        Directory.CreateDirectory("../output");
        File.WriteAllText("../output/index.html", sb.ToString());
    }
}
