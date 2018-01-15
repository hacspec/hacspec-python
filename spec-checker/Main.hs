module Main where

import Language.Python.Common.AST
import Language.Python.Version3.Parser
import System.Environment
import System.Exit
import System.IO

validExpr :: Expr a -> Bool
validExpr _ = False
    
validRaiseExpr :: RaiseExpr a -> Bool
validRaiseExpr _ = False

validStatement :: Statement a -> Bool
-- We assume a specific set of modules is already imported
{-
validStatement (While _ _ _ _) = validWhile
validStatement (For _ _ _ _ _) = validFor
validStatement (Fun _ _ _ _ _) = validFun
validStatement (Conditional _ _ _) = validCond
-}
validStatement (Assign _ _ _) = True -- validAssign
validStatement (AugmentedAssign _ _ _ _) = True --validAssign
validStatement (Assert es _) = False --all validAssert es
{-
validStatement (Decorated _ _ _) = False
-}
validStatement (Return _ _) = True -- validExpr e
validStatement (Raise e _) = validRaiseExpr e
validStatement (Pass _) = True
-- Statements we have no plans to support
validStatement (Import _ _) = False -- We use a fixed set of imports
validStatement (FromImport _ _ _) = False
validStatement (Class _ _ _ _) = False
validStatement (Try _ _ _ _ _) = False
validStatement (With _ _ _) = False
validStatement (Break _) = False
validStatement (Continue _) = False
validStatement (Delete _ _) = False
validStatement (Global _ _) = False
validStatement (NonLocal _ _) = False
validStatement (Print _ _ _ _) = False
validStatement (Exec _ _ _) = False
validStatement _ = False

validSuite :: Suite a -> Bool
validSuite = all validStatement

validParameter :: Parameter a -> Bool
validParameter (Param _ _ Nothing _) = True
validParameter _ = False

validTopStatement :: Statement a -> Bool
validTopStatement (Fun _ ps _ body _) =
  all validParameter ps && validSuite body
validTopStatement _ = False

validModule :: Module a -> Bool
validModule (Module ss) = all validTopStatement ss

exitFail :: String -> IO ()
exitFail msg = hPutStrLn stderr msg >> exitWith (ExitFailure 1)

checkFile :: String -> IO ()
checkFile filename = do
  text <- readFile filename
  case parseModule text filename of
    Left err -> exitFail $ "Parse error: " ++ show err
    Right (m, _) -> do
      putStrLn "Parse succeeded!"
      let status = if validModule m then "valid" else "NOT valid"
      putStrLn $ "Module is " ++ status

main :: IO ()
main = do
  args <- getArgs
  case args of
    [filename] -> checkFile filename
    _ -> exitFail "Usage: spec-checker <filename>"
