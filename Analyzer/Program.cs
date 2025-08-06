using System;
using System.IO;
using System.Text;
using System.Collections.Generic;
using System.Security.Cryptography;

class Program
{
    static string targetDir;


    static void Main()
    {
        string root = Directory.GetCurrentDirectory();
        root = root.Replace("\\Analyzer\\bin\\Debug", "");
        string[] files = Directory.GetFiles(Path.Combine(root, ".."), "*.bin", SearchOption.AllDirectories);
        List<string> list = new List<string>();

        targetDir = Path.Combine(root, "output");
        Directory.CreateDirectory(targetDir);

        Console.WriteLine("Work root: " + root + "!");
        Console.WriteLine("Target dir: " + targetDir + "!");

        foreach (string file in files)
        {
            string rel = file.Replace(root + "/../", "").Replace("\\", "/");
            if (rel.Contains("IoT/BK"))
                list.Add(rel);
        }

        processBekenDumps(list, root);
    }
    public static void processBekenDumps(List<string> list, string root)
    {
        const int chunkSize = 0x1000;
        Dictionary<string, List<string>> groups = new Dictionary<string, List<string>>();
        SHA256 sha = SHA256.Create();

        foreach (string relPath in list)
        {
            string fullPath = Path.Combine(root, "..", relPath);
            byte[] buffer = new byte[chunkSize];

            using (FileStream fs = new FileStream(fullPath, FileMode.Open, FileAccess.Read))
            {
                int bytesRead = fs.Read(buffer, 0, chunkSize);
                if (bytesRead < chunkSize)
                    Array.Resize(ref buffer, bytesRead);
            }

            string hash = BitConverter.ToString(sha.ComputeHash(buffer)).Replace("-", "");

            if (!groups.ContainsKey(hash))
                groups[hash] = new List<string>();
            groups[hash].Add(relPath);
        }

        int groupIndex = 1;
        foreach (var kvp in groups)
        {
            Console.WriteLine($"Group {groupIndex++} ({kvp.Value.Count} files):");
            foreach (string file in kvp.Value)
                Console.WriteLine("  " + file);
            Console.WriteLine();
        }
        Console.WriteLine("Total " + groupIndex + " groups");

        generateHtmlReport(groups);
    }

    public static void generateHtmlReport(Dictionary<string, List<string>> groups)
    {
        StringBuilder sb = new StringBuilder();
        sb.AppendLine("<html><body><h1>Grouped BIN Files by First 0x11000 Bytes</h1>");

        int groupIndex = 1;
        foreach (var kvp in groups)
        {
            sb.AppendFormat("<h2>Group {0} ({1} files)</h2><ul>\n", groupIndex++, kvp.Value.Count);
            foreach (string file in kvp.Value)
                sb.AppendFormat("<li><a href=\"../{0}\">{0}</a></li>\n", file);
            sb.AppendLine("</ul>");
        }

        sb.AppendLine("</body></html>");
        string target = Path.Combine(targetDir,"index.html");
        Console.WriteLine("Raport path "+target);
        File.WriteAllText(target, sb.ToString());
        if(File.Exists(target))
        {
            Console.WriteLine("Raport saved!");
        }
        else
        {
            Console.WriteLine("Failed to save raport!");
        }
    }


}
